from dateutil.relativedelta import relativedelta
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import FormView, UpdateView
from parking.forms import MonthlyProcessingForm, ParkingUpdateForm
from parking.models import ParkingSpace
from parking.services.operate_service import (
    get_latest_active_date,
    get_monthly_empty_counts,
    run_monthly_batch_copy,
)


class MonthlyProcessingView(PermissionRequiredMixin, FormView):
    """月次処理"""

    template_name = "parking/monthly_processing.html"
    form_class = MonthlyProcessingForm
    permission_required = "parking.add_parkingspace"
    success_url = reverse_lazy("parking:management")

    def get_initial(self):
        initial = super().get_initial()
        latest_date = get_latest_active_date()
        if latest_date:
            next_date = latest_date + relativedelta(months=1)
            initial.update({"year": next_date.year, "month": next_date.month})
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["list"] = get_monthly_empty_counts()
        return context

    def form_valid(self, form):
        year = form.cleaned_data["year"]
        month = form.cleaned_data["month"]

        success, message = run_monthly_batch_copy(year, month)
        if success:
            messages.success(self.request, message)
        else:
            messages.warning(self.request, message)

        return redirect(self.get_success_url())


class ParkingUpdateView(PermissionRequiredMixin, UpdateView):
    model = ParkingSpace
    form_class = ParkingUpdateForm
    template_name = "parking/update_form.html"
    permission_required = "parking.add_parkingspace"

    def get_success_url(self):
        return reverse(
            "parking:fig",
            kwargs={"year": self.object.payment_date.year, "month": self.object.payment_date.month},
        )
