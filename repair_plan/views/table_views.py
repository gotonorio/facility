import logging

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views import generic
from facility.services import get_latest_version
from repair_plan.forms import RepairPlanListForm

# from repair_plan.services.pandas_service import (
#     add_total_bottom,
#     get_pandas_table_data,
#     get_pivot_table_data,
#     rename_headers,
#     sort_year_columns,
# )
# from repair_plan.services.table_formatter import add_totals, build_pivot, build_repair_plan_data
from repair_plan.services.table_service import get_repair_plan_table_data

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


# class RepairPlanPandasTableView(PermissionRequiredMixin, generic.TemplateView):
#     """長期修繕計画表（pandas版）"""

#     form_class = RepairPlanListForm
#     permission_required = "repair_plan.add_koujiname"

#     template_name = "repair_plan/table/repairplan_pandas.html"

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)

#         # バージョンの取得
#         ver = self.kwargs.get("version") or self.request.GET.get("version")
#         latest_version, is_manager = get_latest_version(self.request.user)
#         ver = ver or latest_version

#         if not ver:
#             return context

#         # kwargsに"ver"を追加してフォームを初期化する
#         form_kwargs = {"ver": ver}
#         context["form"] = RepairPlanListForm(**form_kwargs)

#         # 1. 修繕計画データからpandasのデータフレーム（DF)を作成。
#         df = get_pandas_table_data(ver)

#         # 2. DFを工事種別でソートしてからピボットテーブルを作成
#         pivot_df = get_pivot_table_data(df)

#         # 3. ピボットテーブルの「年の列」をソート
#         pivot_df = sort_year_columns(pivot_df)

#         # 4. ピボットテーブルの「ヘッダ名」を変更
#         pivot_df = rename_headers(pivot_df)

#         # 5. ピボットテーブルの最下行に合計行を追加
#         pivot_df = add_total_bottom(pivot_df)

#         # ピボットテーブルのList化test
#         dict_list = pivot_df.reset_index().to_dict(orient="records")
#         for row in dict_list:
#             logger.debug(f"Row: {row}")

#         # 工事種別の重複を空にする（上段だけ表示）
#         pivot_df["工事種別"] = pivot_df["工事種別"].mask(pivot_df["工事種別"].duplicated(), "")

#         # 金額フォーマット（カンマ区切り、整数表示）を適用
#         year_columns_total = pivot_df.columns[2:]
#         for col in year_columns_total:
#             pivot_df[col] = pivot_df[col].map("{:,.0f}".format)

#         # HTML生成前に一旦保存
#         html_table = pivot_df.to_html(
#             classes="table is-striped is-size-6 is-narrow is-hoverable repair-table",
#             index=False,
#             border=0,
#             escape=False,
#         )
#         context["html_table"] = html_table

#         return context

#     # ------------------------------------------------------------
#     # 以下は、pandasのto_htmlを使わない従来の方法での実装例
#     # ------------------------------------------------------------

#     # template_name = "repair_plan/table/repairplan_pandas_test.html"

#     # def get_context_data(self, **kwargs):
#     #     context = super().get_context_data(**kwargs)

#     #     # ----------------------
#     #     # バージョンの決定
#     #     # ----------------------
#     #     ver = self.kwargs.get("version") or self.request.GET.get("version")
#     #     latest_version, is_manager = get_latest_version(self.request.user)
#     #     ver = ver or latest_version

#     #     if not ver:
#     #         return context

#     #     # kwargsに"ver"を追加
#     #     form_kwargs = {"ver": ver}
#     #     context["form"] = RepairPlanListForm(**form_kwargs)

#     #     # 1. 修繕計画データからpandasのデータフレーム（DF)を作成
#     #     df = get_pandas_table_data(ver)

#     #     # 2. DFを工事種別でソートしてからピボットテーブルを作成
#     #     pivot_df = build_pivot(df)

#     #     # 10. ピボットテーブルに合計行を追加
#     #     pivot_df, yearly_total = add_totals(pivot_df)

#     #     repair_plan_data = build_repair_plan_data(pivot_df, yearly_total)

#     #     context.update(repair_plan_data)

#     #     return context
