import logging

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views import generic
from facility.services import get_latest_version
from repair_plan_cycle.form import CycleDataListForm
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

        if kwargs:
            # update後にget_success_url()で遷移する場合、kwargsにデータが渡される。typeはint)
            ver = str(kwargs.get("version"))
        else:
            ver = self.request.GET.get("version", False)

        # 修繕計画のバージョンとユーザの管理者権限
        latest_version, is_manager = get_latest_version(self.request.user)
        # バージョン選択の処理
        if ver is False or ver is None:
            ver = latest_version
        # qs = KoujiCycleData.objects.filter(version=version_id).order_by("kouji_type", "first_year")
        qs = KoujiCycleData.objects.filter(version=ver).order_by("kouji_type", "first_year")

        # form = CycleDataListForm(initial={"version": version_id})
        form = CycleDataListForm(initial={"version": ver})
        context["form"] = form
        # 追加したいデータをcontextへセット
        context["cycledata_list"] = qs
        context["version_no"] = ver
        return context
