import logging

from bicycle.forms import BicycleSpaseListForm
from bicycle.models import BicycleSpace
from bicycle.services.display_service import (
    get_bicycle_by_room,
    get_bicycle_fee_by_room,
    get_bicycle_income_summary,
    get_bicycle_summary,
)
from common.forms.base_form import YearMonthForm
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.utils import timezone
from django.utils.timezone import localtime
from django.views.generic import ListView, TemplateView

logger = logging.getLogger(__name__)


class BicycleSpaceListView(LoginRequiredMixin, TemplateView):
    """駐輪場一覧"""

    template_name = "bicycle/bicycle_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        local_now = localtime(timezone.now())

        # 日付の取得
        year = self.kwargs.get("year") or self.request.GET.get("year", local_now.year)
        month = self.kwargs.get("month") or self.request.GET.get("month", local_now.month)

        # Serviceでデータ取得
        categorized, total, _ = get_bicycle_summary(year, month)

        context.update(
            {
                "form": BicycleSpaseListForm(initial={"year": year, "month": month}),
                "total": total,
                "title": f"{year}年 {month}月",
                "year": year,
                "month": month,
                **categorized,  # space1 ~ space4 を展開
            }
        )
        return context


class BicycleSpaceByRoomView(BicycleSpaceListView):
    """住戸別駐輪場一覧"""

    template_name = "bicycle/bicyclespace_by_room.html"

    def get_context_data(self, **kwargs):
        # 親の共通処理（日付取得等）を活かしつつ、中身を差し替え
        context = super().get_context_data(**kwargs)
        qs, total = get_bicycle_by_room(context["year"], context["month"])
        context.update({"bicycle_list": qs, "total": total})
        return context


class BicycleSpaceFeeByRoomView(BicycleSpaceListView):
    """住戸別駐輪場使用料（管理者用）"""

    template_name = "bicycle/bicyclespacefee_by_room.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qs, total = get_bicycle_fee_by_room(context["year"], context["month"])
        context.update({"bicycle_list": qs, "total": total})
        return context


class BicycleIncomeHistoryView(LoginRequiredMixin, ListView):
    """駐輪場収入履歴一覧"""

    model = BicycleSpace
    template_name = "bicycle/bicycleincome_history.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        year = self.request.GET.get("year", localtime(timezone.now()).year)

        qs, total = get_bicycle_income_summary(year)

        context.update(
            {
                "bicycle": qs,
                "total": total,
                "form": YearMonthForm(initial={"year": year}),
            }
        )
        return context


class NewContractView(PermissionRequiredMixin, TemplateView):
    """新規契約の表示"""

    template_name = "bicycle/new_contract.html"
    permission_required = "parking.add_parkingspace"
    raise_exception = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        local_now = localtime(timezone.now())

        # 日付の取得
        year = self.request.GET.get("year", local_now.year)
        month = self.request.GET.get("month", local_now.month)

        context["form"] = BicycleSpaseListForm(initial={"year": year, "month": month})

        # 新規契約
        context["new_contract"] = BicycleSpace.objects.get_new_contact(int(year), int(month))
        # 解約
        context["new_cancel"] = BicycleSpace.objects.get_new_cancel(int(year), int(month))

        return context
