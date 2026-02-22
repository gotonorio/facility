import logging

from django.conf import settings
from repair_plan_simulator.models import Shuuzenhi_income

logger = logging.getLogger(__name__)


def add_income_list(shuuzenhi_expense, sim_data, zandaka) -> list:
    """shuuzenhi_expenseに修繕会計の収入を追加
    - 完了した工事の実支出金額をその年の収入から減じる。
    """
    shuuzenhi_rate = sim_data["shuuzenhi_rate"]
    parking_rate = sim_data["parking_rate"]
    data_list = []
    ruikei = zandaka

    # 最新の収入見込みデータ。real=Falseのデータがあればその年以降の収入データは無視する。
    obj = Shuuzenhi_income.objects.filter(real=False).order_by("-year").first()
    if obj:
        qs_income = Shuuzenhi_income.objects.filter(year__lte=obj.year).order_by("year")
        income_last = qs_income.last()
        last_year = obj.year
    else:
        qs_income = Shuuzenhi_income.objects.filter(real=True).order_by("year")
        income_last = qs_income.last()
        last_year = income_last.year

    # querysetの結果をdict要素としたlistに変換
    list_income = tolist_income_list(qs_income)

    # 修繕積立金
    last_income = shuuzenhi_rate * income_last.income
    # 駐車場会計からの収入
    last_parking_income = parking_rate * income_last.parking_income
    # その他収入
    last_extra_income = income_last.extra_income
    # 駐車場会計から支出する定期保守費
    last_parking_kanrihi = 0

    # ToDo 長期修繕計画の支出でループすると、支出のない年がスキップされ、その年の収入が加算されない。
    # 現在のところは、支出のない年には支出金額0のダミー工事を設定するようにしている。
    # マスタデータの初年度修繕資産の年からループを開始する。
    for y in shuuzenhi_expense:
        yyyy = y["kouji_year"]
        # 年度毎に収入データを追加する。
        for d in list_income:
            if d["year"] == yyyy:
                # 収入見込みデータ（実績収入データ）が設定されている年はその年のデータを使う。
                income = d["income"] * shuuzenhi_rate
                parking_income = d["parking_income"] * parking_rate
                extra_income = d["extra_income"]
                parking_kanrihi = d["parking_kanrihi"]
                y["shuuzenhi_income"] = income
                y["parking_income"] = parking_income - parking_kanrihi
                y["extra_income"] = extra_income
                y["parking_kanrihi"] = parking_kanrihi
                y["income"] = income + parking_income + extra_income
                y["income"] -= parking_kanrihi
            elif yyyy > last_year:
                # 修繕積立金データ等の収入見込みデータが設定されていない年度は最新の収入データとする。
                y["shuuzenhi_income"] = last_income
                y["parking_income"] = last_parking_income - last_parking_kanrihi
                y["extra_income"] = last_extra_income
                y["parking_kanrihi"] = last_parking_kanrihi
                y["income"] = last_income + last_parking_income + last_extra_income
                y["income"] -= last_parking_kanrihi
        ruikei += y["income"]
        y["income_ruikei"] = ruikei
        data_list.append(y)

    return shuuzenhi_expense


def tolist_income_list(shuuzenhi_income_qs) -> list:
    """修繕会計の収入見込みクエリセットをリストに変換する"""
    income_list = []
    for income in shuuzenhi_income_qs:
        row = {}
        row["year"] = income.year
        row["income"] = income.income
        row["parking_income"] = income.parking_income
        row["extra_income"] = income.extra_income
        row["parking_kanrihi"] = income.parking_kanrihi
        income_list.append(row)

    # 連続した年数のデータにするため、欠損している年度のデータを補完する。
    if income_list:
        start_year = income_list[0]["year"]
        end_year = income_list[-1]["year"]
        full_income_list = []
        income_dict = {item["year"]: item for item in income_list}
        for year in range(start_year, end_year + 1):
            if year in income_dict:
                full_income_list.append(income_dict[year])
            else:
                # 欠損している年度のデータを追加(欠損以前の存在する年度データで保管する）)
                full_income_list = fill_years_with_previous_value(income_list)
        income_list = full_income_list

    return income_list


# 欠損している年度のデータを追加(欠損以前の存在する年度データで保管する）
def fill_years_with_previous_value(data):
    """
    year が不連続なリストを、直前の val で補完して連続化する
    """
    # year 昇順にソート
    sorted_data = sorted(data, key=lambda x: x["year"])

    result = []
    prev_income = None
    prev_parking_income = None
    prev_extra_income = None
    prev_parking_kanrihi = None

    for i in range(len(sorted_data) - 1):
        current = sorted_data[i]
        next_item = sorted_data[i + 1]

        result.append(current)
        prev_income = current["income"]
        prev_parking_income = current["parking_income"]
        prev_extra_income = current["extra_income"]
        prev_parking_kanrihi = current["parking_kanrihi"]

        # 欠けている year を補完
        for year in range(current["year"] + 1, next_item["year"]):
            result.append(
                {
                    "year": year,
                    "income": prev_income,
                    "parking_income": prev_parking_income,
                    "extra_income": prev_extra_income,
                    "parking_kanrihi": prev_parking_kanrihi,
                }
            )

    # 最後の要素を追加
    result.append(sorted_data[-1])

    return result
