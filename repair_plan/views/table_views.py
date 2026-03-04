import logging

import pandas as pd
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views import generic
from facility.services import get_latest_version
from repair_plan.forms import RepairPlanListForm
from repair_plan.services.table_formatter import build_repair_plan_data
from repair_plan.services.table_service import (
    get_pandas_table_data,
    get_pivot_table_data,
    get_repair_plan_table_data,
)

logger = logging.getLogger(__name__)


class RepairPlanTableView(PermissionRequiredMixin, generic.TemplateView):
    """長期修繕計画表（詳細版）"""

    template_name = "repair_plan/table/repairplan_table.html"
    permission_required = "repair_plan.add_koujiname"
    is_simple = False  # 子クラスで上書き

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # バージョンの決定
        ver = self.kwargs.get("version") or self.request.GET.get("version")
        latest_version, is_manager = get_latest_version(self.request.user)
        ver = ver or latest_version

        if not ver:
            return context

        # kwargsに"ver"を追加
        form_kwargs = {"ver": ver}
        context["form"] = RepairPlanListForm(**form_kwargs)

        # Service層で複雑な計算を実行
        data = get_repair_plan_table_data(ver, is_simple=self.is_simple)

        if data:
            context.update(
                {
                    "repairplan_list": data["repairplan_list"],
                    "total": data["year_total"],
                    "all_total": data["all_total"],
                    "year": data["years"],
                }
            )

        return context


class RepairPlanSimpleTableView(RepairPlanTableView):
    """長期修繕計画表（シンプル版）"""

    template_name = "repair_plan/repairplan_simpletable.html"
    permission_required = "repair_plan.view_koujiname"
    is_simple = True  # ロジックを切り替え


class RepairPlanPandasTableView(PermissionRequiredMixin, generic.TemplateView):
    """長期修繕計画表（pandas版）"""

    form_class = RepairPlanListForm
    permission_required = "repair_plan.add_koujiname"

    template_name = "repair_plan/table/repairplan_pandas.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # バージョンの取得
        ver = self.kwargs.get("version") or self.request.GET.get("version")
        latest_version, is_manager = get_latest_version(self.request.user)
        ver = ver or latest_version

        if not ver:
            return context

        # kwargsに"ver"を追加してフォームを初期化する
        form_kwargs = {"ver": ver}
        context["form"] = RepairPlanListForm(**form_kwargs)

        # 修繕計画データからpandasのデータフレーム（DF)を作成
        df = get_pandas_table_data(ver)

        # DFを工事種別でソートしてからピボットテーブルを作成
        pivot_df = get_pivot_table_data(df)

        # ピボットテーブルの最後列に行合計を追加(axis=1は行方向の合計)
        year_columns = pivot_df.columns[2:]
        pivot_df["合計"] = pivot_df[year_columns].sum(axis=1)

        # ピボットテーブルの最下行に年ごとの合計を追加(axis=0は列方向の合計)
        year_totals = pivot_df[year_columns].sum(axis=0)
        # ピボットテーブルの総合計を計算(年ごとの合計の合計)
        grand_total = pivot_df["合計"].sum(axis=0)

        total_row = {
            "工事種別": "",
            "工事名": "総合計",
            **year_totals.to_dict(),
            "合計": grand_total,
        }
        # ピボットテーブルの最下行に合計行を追加
        pivot_df = pd.concat([pivot_df, pd.DataFrame([total_row])], ignore_index=True)

        # 工事種別の重複を空にする（上段だけ表示）
        pivot_df["工事種別"] = pivot_df["工事種別"].mask(pivot_df["工事種別"].duplicated(), "")

        # # 種別が変わる行を判定
        # pivot_df["is_category_row"] = pivot_df["工事種別"] != ""

        # 金額フォーマット
        for col in year_columns:
            pivot_df[col] = pivot_df[col].map("{:,.0f}".format)

        # HTML生成前に一旦保存
        # # pivot_df = pivot_df.drop(columns=["is_category_row"], errors="ignore")
        html_table = pivot_df.to_html(
            classes="table is-striped is-size-6 is-narrow is-hoverable repair-table",
            index=False,
            border=0,
            escape=False,
        )
        context["html_table"] = html_table

        return context

    # ------------------------------------------------------------
    # 以下は、pandasを使わない従来の方法での実装例（コメントアウト）
    # ------------------------------------------------------------

    # template_name = "repair_plan/table/repairplan_pandas_test.html"

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)

    #     # ----------------------
    #     # バージョンの決定
    #     # ----------------------
    #     ver = self.kwargs.get("version") or self.request.GET.get("version")
    #     latest_version, is_manager = get_latest_version(self.request.user)
    #     ver = ver or latest_version

    #     if not ver:
    #         return context

    #     # kwargsに"ver"を追加
    #     form_kwargs = {"ver": ver}
    #     context["form"] = RepairPlanListForm(**form_kwargs)

    #     # ---------------------------
    #     # pandasのデータフレームを取得
    #     # ---------------------------
    #     df = get_pandas_table_data(ver)
    #     df = df.sort_values(["kouji_type__sequense", "kouji_name"])

    #     repair_plan_data = build_repair_plan_data(df)

    #     context.update(repair_plan_data)

    #     return context
