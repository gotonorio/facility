# repair_plan_simulator/views/simulate_views.py
# -----------------------------------------------------------------------------
# シミュレーション実行画面
# -----------------------------------------------------------------------------

import logging

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import FormView
from facility.services import get_latest_version
from repair_plan.models import KoujiName, MasterPlan

from repair_plan_simulator.forms import SimulateDataForm
from repair_plan_simulator.services import simulator

logger = logging.getLogger(__name__)


class SimulateView(LoginRequiredMixin, FormView):
    """シミュレーション実行画面"""

    template_name = "repair_plan_simulator/simulate_pc.html"
    form_class = SimulateDataForm
    only_manager = False

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        _, self.only_manager = get_latest_version(self.request.user)
        kwargs["only_manager"] = self.only_manager
        return kwargs

    def get_template_names(self):
        if self.request.user_agent_flag == "mobile":
            return ["repair_plan_simulator/simulate_pc.html"]
        return ["repair_plan_simulator/simulate_pc.html"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        ver_str = self.request.GET.get("keikaku_ver")

        if ver_str:
            plan = MasterPlan.objects.get(version=int(ver_str))
            ver_int = plan.version
        else:
            ver_int = None

        if ver_int:
            sim_data = {
                "ver": ver_str,
                "expense_rate": float(self.request.GET.get("expense_rate")),
                "sales_tax_rate": float(self.request.GET.get("sales_tax_rate")),
                "shuuzenhi_rate": float(self.request.GET.get("shuuzenhi_rate")),
                "parking_rate": float(self.request.GET.get("parking_rate")),
                "cpi_flg": self.request.GET.get("cpi_flg"),
            }

            form = SimulateDataForm(
                self.only_manager,
                initial={
                    "keikaku_ver": ver_str,
                    "expense_rate": sim_data["expense_rate"],
                    "sales_tax_rate": sim_data["sales_tax_rate"],
                    "shuuzenhi_rate": sim_data["shuuzenhi_rate"],
                    "parking_rate": sim_data["parking_rate"],
                    "cpi_flg": sim_data["cpi_flg"],
                },
            )

            expense = simulator.calc_expense_list(
                ver_str,
                sim_data["expense_rate"],
                sim_data["sales_tax_rate"],
                sim_data["cpi_flg"],
            )

            balance = MasterPlan.objects.filter(version=ver_int).values("balance")[0]["balance"]
            logger.debug(f"SimulateView get_context_data balance={balance}")

            simulate_data = simulator.add_income_list(expense, sim_data, balance)
            excluded_data = KoujiName.objects.filter(version__version=ver_int, do_calc=False)

            context.update(
                {
                    "simulate_data": simulate_data,
                    "form": form,
                    "excluded_data": excluded_data,
                    "start_year": -settings.INITIAL_YEAR,
                    "version": ver_str,
                }
            )

        return context
