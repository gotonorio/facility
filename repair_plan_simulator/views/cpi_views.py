# -----------------------------------------------------------------------------
# 物価指数の作成・更新
# -----------------------------------------------------------------------------

import logging

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import CreateView, UpdateView

from repair_plan_simulator.forms import CPICreateForm
from repair_plan_simulator.models import ConsumerPriceIndex

logger = logging.getLogger(__name__)


class CreateCPIView(PermissionRequiredMixin, CreateView):
    model = ConsumerPriceIndex
    form_class = CPICreateForm
    template_name = "repair_plan_simulator/cpi_form.html"
    permission_required = "repair_plan.add_koujiname"
    raise_exception = True

    def get_success_url(self):
        return reverse("repair_plan_simulator:create_cpi")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cpi_list"] = ConsumerPriceIndex.objects.all().order_by("year")
        return context


class UpdateCPIView(PermissionRequiredMixin, UpdateView):
    model = ConsumerPriceIndex
    form_class = CPICreateForm
    template_name = "repair_plan_simulator/cpi_form.html"
    permission_required = "repair_plan.add_koujiname"
    raise_exception = True

    def get_success_url(self):
        return reverse("repair_plan_simulator:create_cpi")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cpi_list"] = ConsumerPriceIndex.objects.all().order_by("year")
        return context

    def form_valid(self, form):
        continuas = form.cleaned_data["continuas"]

        if continuas:
            this_year = form.cleaned_data["year"]
            cpi = form.cleaned_data["cpi"]
            comment = form.cleaned_data["comment"]
            last_year = ConsumerPriceIndex.get_lastyear()["last_year"]
            ConsumerPriceIndex.save_continuas_cpi(this_year, last_year, cpi, comment)
        else:
            super().form_valid(form)

        return redirect(self.get_success_url())
