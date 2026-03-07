from bicycle.forms import BicycleUpdateForm, MonthlyProcessingForm
from bicycle.models import BicycleSpace
from bicycle.services.operate_service import (
    get_latest_bicycle_date,
    get_monthly_bicycle_empty_counts,
    run_bicycle_monthly_processing,
)
from dateutil.relativedelta import relativedelta
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.utils.http import urlencode
from django.views.generic import FormView, UpdateView


class BicycleSpaceUpdateView(PermissionRequiredMixin, UpdateView):
    """駐輪場データのUPDATE"""

    model = BicycleSpace
    form_class = BicycleUpdateForm
    template_name = "bicycle/update_form.html"
    permission_required = "parking.add_parkingspace"
    raise_exception = True

    def get_success_url(self):
        base_url = reverse("bicycle:list")
        params = urlencode(
            {
                "year": self.object.date.year,
                "month": self.object.date.month,
            }
        )
        return f"{base_url}?{params}"


class MonthlyProcessingView(PermissionRequiredMixin, FormView):
    """月次処理"""

    template_name = "bicycle/monthly_processing.html"
    form_class = MonthlyProcessingForm
    permission_required = "parking.add_parkingspace"
    raise_exception = True
    success_url = reverse_lazy("bicycle:list")

    def get_initial(self):
        """Serviceから最新日付を取得し、翌月分を初期値にする"""
        initial = super().get_initial()
        latest_date = get_latest_bicycle_date()
        if latest_date:
            next_date = latest_date + relativedelta(months=1)
            initial.update({"year": next_date.year, "month": next_date.month})
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Serviceから登録済みリストを取得
        context["list"] = get_monthly_bicycle_empty_counts()
        return context

    def form_valid(self, form):
        """バリデーション成功後にServiceでコピー処理を実行"""
        year = form.cleaned_data["year"]
        month = form.cleaned_data["month"]

        success, message = run_bicycle_monthly_processing(year, month)
        if success:
            messages.success(self.request, message)
        else:
            messages.info(self.request, message)

        return redirect(self.get_success_url())
