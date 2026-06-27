from dateutil.relativedelta import relativedelta
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.utils.http import urlencode
from django.views.generic import FormView, UpdateView
from motorcycle.forms import MonthlyProcessingForm, MotorCycleUpdateForm
from motorcycle.models import MotorCycleSpace
from motorcycle.services.operate_service import (
    get_latest_motorcycle_date,
    get_monthly_motorcycle_empty_list,
    run_motorcycle_monthly_copy,
)


class MotorCycleSpaceUpdateView(PermissionRequiredMixin, UpdateView):
    """バイク置場データのUPDATE"""

    model = MotorCycleSpace
    form_class = MotorCycleUpdateForm
    template_name = "motorcycle/update_form.html"
    permission_required = "parking.add_parkingspace"
    raise_exception = True

    def get_success_url(self):
        base_url = reverse("motorcycle:list")
        params = urlencode(
            {
                "year": self.object.date.year,
                "month": self.object.date.month,
            }
        )
        return f"{base_url}?{params}"


class MonthlyProcessingView(PermissionRequiredMixin, FormView):
    """月次処理"""

    template_name = "motorcycle/monthly_processing_form.html"
    form_class = MonthlyProcessingForm
    permission_required = "parking.add_parkingspace"
    raise_exception = True
    success_url = reverse_lazy("motorcycle:list")

    def get_initial(self):
        """初期表示の年月をServiceから取得"""
        initial = super().get_initial()
        latest_date = get_latest_motorcycle_date()
        if latest_date:
            next_date = latest_date + relativedelta(months=1)
            initial.update({"year": next_date.year, "month": next_date.month})
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Serviceから登録済みリストを取得
        context["list"] = get_monthly_motorcycle_empty_list()
        return context

    def form_valid(self, form):
        """Serviceで一括生成を実行"""
        year = form.cleaned_data["year"]
        month = form.cleaned_data["month"]

        success, message = run_motorcycle_monthly_copy(year, month)
        if success:
            messages.success(self.request, message)
        else:
            messages.info(self.request, message)

        return redirect(self.get_success_url())
