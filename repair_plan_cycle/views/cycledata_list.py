import logging

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views import generic
from repair_plan_cycle.form import CycleDataListForm
from repair_plan_cycle.models import KoujiCycleData
from repair_plan_cycle.services.cycledata_list_service import get_cycledata, get_cycledata_latest_version

logger = logging.getLogger(__name__)


class CycleDataListView(PermissionRequiredMixin, generic.ListView):
    """修繕工事の周期データを表示"""

    model = KoujiCycleData
    template_name = "repair_plan_cycle/cycledata_list.html"
    permission_required = "repair_plan.add_koujiname"
    # ListViewでは context_object_name を指定するとテンプレートで使いやすくなる
    context_object_name = "cycledata_list"

    def get_queryset(self):
        """メインのデータリストを取得（フィルタリングを担当）"""
        # 1. パラメータ取得
        self.ver_param = self.kwargs.get("version") or self.request.GET.get("version")

        # 2. Service呼び出し
        # ここでフィルタリングした結果が、自動的に context['cycledata_list'] に入る
        self.version_obj = get_cycledata_latest_version(self.ver_param)
        qs = get_cycledata(self.version_obj)
        return qs

    def get_context_data(self, **kwargs):
        """メインリスト以外の「追加データ（フォーム等）」をセットする"""
        context = super().get_context_data(**kwargs)
        # フォームとバージョン番号だけを追加
        context["form"] = CycleDataListForm(initial={"version": self.version_obj})
        return context
