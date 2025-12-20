import logging

from django.db.models import ExpressionWrapper, F, IntegerField
from django.db.models.aggregates import Sum
from repair_plan.models import KoujiName
from repair_plan_simulator.models import ConsumerPriceIndex

logger = logging.getLogger(__name__)


def calc_cpi(plan_list) -> list:
    """物価指数を考慮する"""
    qs = ConsumerPriceIndex.objects.all().order_by("year")
    if qs:
        for plan_data in plan_list:
            for cpi in qs:
                if plan_data["kouji_year"] == cpi.year:
                    # Decimal型をFloat型に変換しておく。
                    plan_data["cost"] *= float(cpi.cpi)
                    break
    return plan_list


def calc_expense_list(ver, expense_rate, sales_tax_rate, cpi_flg) -> list:
    """長期修繕計画支出額を年度毎に集計したリストを返す
    - 完了工事の計画支出を0とする。
    - F()式の列が異なるデータ型(integer,float)のため、ExpressionWrapper()を使う。
    - (1) values().annotate()（SQLのBROUP BY）で計画支出金額、実支出金額の行集計を行う。
    - (2) values().annotate()で完了した工事について修繕計画の行集計を行う。
    - (3) 年度毎に「予定支出金額」から「実支出金額」を差し引く処理を行う。
    """
    # (1) 長期修繕計画の計画支出、完了工事の実支出を年度毎に集計したリスト
    plan_qs = (
        KoujiName.objects.filter(version__version=ver, do_calc=True)
        .values("kouji_year")
        .annotate(
            cost=ExpressionWrapper(Sum(F("unit_price") * F("kouji_quantity")), output_field=IntegerField()),
            actual_cost=Sum("actual_cost"),
        )
    ).order_by("kouji_year")
    # querysetの結果をdict要素としたlistに変換
    plan_list = list(plan_qs)

    # 計画値に物価指数を反映する。
    if cpi_flg == "on":
        plan_list = calc_cpi(plan_list)

    # (2) 完了した工事の計画支出額を年度毎に集計したリスト
    qs_complete = (
        KoujiName.objects.filter(version__version=ver, complete=True, do_calc=True)
        .values("kouji_year")
        .annotate(
            cost=ExpressionWrapper(Sum(F("unit_price") * F("kouji_quantity")), output_field=IntegerField()),
        )
    )
    # querysetの結果をdict要素としたlistに変換
    complete_list = list(qs_complete)

    # (3) 完了した工事の計画支出額から完了工事の実支出金額を減じる。
    for complete in complete_list:
        for plan in plan_list:
            if complete["kouji_year"] == plan["kouji_year"]:
                plan["cost"] -= complete["cost"]
                break

    # (4) 経費と消費税を考慮した計画値と実支出額のリストを作成。
    ruikei = 0
    expense_list = []
    for plan in plan_list:
        row = {}
        # 経費率、消費税率を考慮した年度支出額
        cost = plan["cost"] * (1 + 0.01 * expense_rate) * (1 + 0.01 * sales_tax_rate)
        # dict要素としての年度
        row["kouji_year"] = plan["kouji_year"]
        # dict要素としての計画支出額（年度毎）
        row["cost"] = cost
        # dict要素として、完了工事の実支出額
        row["actual_cost"] = plan["actual_cost"]
        # dict要素としての累計計画支出額（年度毎）
        ruikei += cost + plan["actual_cost"]
        row["ruikei_cost"] = ruikei
        expense_list.append(row)
    return expense_list
