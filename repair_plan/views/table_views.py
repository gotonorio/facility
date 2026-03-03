import logging

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views import generic
from facility.services import get_latest_version
from repair_plan.forms import RepairPlanListForm
from repair_plan.services.table_service import get_repair_plan_table_data

logger = logging.getLogger(__name__)


class RepairPlanTableView(PermissionRequiredMixin, generic.TemplateView):
    """長期修繕計画表（詳細版）"""

    template_name = "repair_plan/repairplan_table.html"
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
