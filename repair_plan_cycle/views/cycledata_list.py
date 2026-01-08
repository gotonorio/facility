import logging

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views import generic
from repair_plan_cycle.form import CycleDataListForm
from repair_plan_cycle.models import KoujiCycleData

logger = logging.getLogger(__name__)


class CycleDataListView(PermissionRequiredMixin, generic.ListView):
    """修繕工事の周期データを表示"""

    model = KoujiCycleData
    template_name = "repair_plan_cycle/cycledata_list.html"
    permission_required = "repair_plan.add_koujiname"
    # ListViewでは context_object_name を指定するとテンプレートで使いやすくなります
    context_object_name = "cycledata_list"

    def get_version(self):
        """URL引数(kwargs)またはGETパラメータからversionを取得する共通メソッド"""
        # self.kwargs は URLパス内の変数、self.request.GET は ?version=... の変数
        return self.kwargs.get("version") or self.request.GET.get("version")

    def get_queryset(self):
        """メインのデータリストを取得（フィルタリングを担当）"""
        ver = self.get_version()
        # ここでフィルタリングした結果が、自動的に context['cycledata_list'] に入ります
        return KoujiCycleData.objects.filter(version=ver).order_by("kouji_type", "first_year")

    def get_context_data(self, **kwargs):
        """メインリスト以外の「追加データ（フォーム等）」をセットする"""
        context = super().get_context_data(**kwargs)
        ver = self.get_version()

        # フォームとバージョン番号だけを追加
        context["form"] = CycleDataListForm(initial={"version": ver})
        context["version_no"] = ver
        return context

    # model = KoujiCycleData
    # template_name = "repair_plan_cycle/cycledata_list.html"
    # permission_required = "repair_plan.add_koujiname"

    # def get_context_data(self, **kwargs):
    #     # 既存のcontextをまず取得
    #     context = super().get_context_data(**kwargs)

    #     if kwargs:
    #         # update後にget_success_url()で遷移する場合、kwargsにデータが渡される。typeはint)
    #         ver = str(kwargs.get("version"))
    #     else:
    #         ver = self.request.GET.get("version", False)

    #     qs = KoujiCycleData.objects.filter(version=ver).order_by("kouji_type", "first_year")
    #     form = CycleDataListForm(initial={"version": ver})

    #     context["form"] = form
    #     # 追加したいデータをcontextへセット
    #     context["cycledata_list"] = qs
    #     context["version_no"] = ver
    #     return context
