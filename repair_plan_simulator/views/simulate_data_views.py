from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from repair_plan.models import MasterPlan

from repair_plan_simulator.models import ConsumerPriceIndex, Shuuzenhi_income


# ----------------------------------------------------------------------------
# シミュレーション計算用の収入データ一覧表示
# ----------------------------------------------------------------------------
class SimulateDataView(LoginRequiredMixin, TemplateView):
    """シミュレーションの基礎データ一覧"""

    template_name = "repair_plan_simulator/simulate_data.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["master_data"] = MasterPlan.objects.all().order_by("-version")
        context["income_data"] = Shuuzenhi_income.objects.all().order_by("-year")
        context["cpi_data"] = ConsumerPriceIndex.objects.order_by("year")

        return context
