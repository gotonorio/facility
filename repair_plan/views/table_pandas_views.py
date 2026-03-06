import logging

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic import TemplateView
from facility.services import get_latest_version
from repair_plan.forms import RepairPlanListForm
from repair_plan.services.pandas_service import (
    add_total_last,
    bottom_total_list,
    get_pandas_dadaframe,
    get_pandas_pivottable,
    rename_headers,
    sort_year_columns,
)

logger = logging.getLogger(__name__)


class RepairPlanPandasView(PermissionRequiredMixin, TemplateView):
    """長期修繕計画表（pandas版）"""

    form_class = RepairPlanListForm
    permission_required = "repair_plan.add_koujiname"
    template_name = "repair_plan/table/repairplan_table_pandas.html"

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

        # 1. 修繕計画データからpandasのデータフレーム（DF)を作成。
        df = get_pandas_dadaframe(ver)

        # 2. DFを工事種別でソートしてからピボットテーブルを作成
        pivot_df = get_pandas_pivottable(df)

        # 3. ピボットテーブルの「年の列」をソート
        pivot_df = sort_year_columns(pivot_df)

        # 4. ピボットテーブルの「ヘッダ名」を変更
        pivot_df = rename_headers(pivot_df)

        # 5. ピボットテーブルの最後列に合計を追加
        pivot_df = add_total_last(pivot_df)

        # 工事種別の重複を空にする（上段だけ表示）
        pivot_df["工事種別"] = pivot_df["工事種別"].mask(pivot_df["工事種別"].duplicated(), "")

        # ----------------------------------------
        # ピボットテーブルデータのList化
        # ----------------------------------------
        # ヘッダーをlistとして取り出す
        header_list = pivot_df.columns.to_list()
        # データ本体のvalueをlistとするlistを作成する。
        values_list = pivot_df.reset_index().values[:, 1:].tolist()
        # 最下行の合計行を作成する
        total = bottom_total_list(pivot_df)

        context.update({"repair_plan_list": values_list, "year": header_list, "total": total})

        return context
