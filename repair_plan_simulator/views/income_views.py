# repair_plan_simulator/views/income_views.py
# -----------------------------------------------------------------------------
# 修繕会計収入の作成・更新
# -----------------------------------------------------------------------------

import logging

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse
from django.views.generic import CreateView, UpdateView

from repair_plan_simulator.forms import ShuuzenhiIncomeCreateForm
from repair_plan_simulator.models import Shuuzenhi_income

logger = logging.getLogger(__name__)


class CreateIncomeView(PermissionRequiredMixin, CreateView):
    model = Shuuzenhi_income
    form_class = ShuuzenhiIncomeCreateForm
    template_name = "repair_plan_simulator/income_form.html"
    permission_required = "repair_plan.add_koujiname"
    raise_exception = True

    def get_success_url(self):
        return reverse("repair_plan_simulator:create_income")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["masterlist"] = Shuuzenhi_income.objects.all().order_by("-year")
        return context


class UpdateIncomeView(PermissionRequiredMixin, UpdateView):
    model = Shuuzenhi_income
    form_class = ShuuzenhiIncomeCreateForm
    template_name = "repair_plan_simulator/income_form.html"
    permission_required = "repair_plan.add_koujiname"
    raise_exception = True

    def get_success_url(self):
        return reverse("repair_plan_simulator:create_income")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["masterlist"] = Shuuzenhi_income.objects.all().order_by("-year")
        return context
