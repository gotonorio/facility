import logging

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views import generic
from repair_plan_cycle.form import KoujiCycleDataListForm
from repair_plan_cycle.models import KoujiCycleData

logger = logging.getLogger(__name__)


class KoujiCycleDataListView(PermissionRequiredMixin, generic.ListView):
    """修繕工事の周期データを表示"""

    model = KoujiCycleData
    template_name = "repair_plan_cycle/cycledata_list.html"
    permission_required = "repair_plan.add_koujiname"

    def get_context_data(self, **kwargs):
        # 既存のcontextをまず取得
        context = super().get_context_data(**kwargs)
        version_id = self.request.GET.get("version", 0)

        qs = KoujiCycleData.objects.filter(version=version_id).order_by("kouji_type", "first_year")

        form = KoujiCycleDataListForm(initial={"version": version_id})
        context["form"] = form
        # 追加したいデータをcontextへセット
        context["cycledata_list"] = qs
        return context
