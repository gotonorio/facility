from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import redirect
from django.utils import timezone
from django.utils.timezone import localtime
from django.views.generic import ListView, TemplateView
from facility.forms import IncomeHistoryForm
from parking.forms import ParkingSpaceFigForm, ParkingSpaceListForm
from parking.models import ParkingSpace
from parking.services.display_service import (
    categorize_parking_spaces,
    get_income_history_metrics,
    get_parking_diagram_data,
    get_parking_summary,
    get_utilization_metrics,
)


class ParkingSpaceListView(LoginRequiredMixin, ListView):
    """一般ユーザ用 駐車場リスト表示"""

    model = ParkingSpace
    template_name = "parking/parking_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        local_now = localtime(timezone.now())
        year = self.request.GET.get("year", local_now.year)
        month = self.request.GET.get("month", local_now.month)

        # Service層で集計
        qs, total = get_parking_summary(year, month)
        space1, space2, space3 = categorize_parking_spaces(qs)

        context.update(
            {
                "total": total,
                "form": ParkingSpaceListForm(initial={"year": year, "month": month}),
                "title": f"{year}年 {month}月",
                "space1": space1,
                "space2": space2,
                "space3": space3,
            }
        )
        return context


class ParkingFigView(LoginRequiredMixin, ListView):
    """空き駐車場の図解表示"""

    model = ParkingSpace
    context_object_name = "parkings"

    def get_template_names(self):
        if self.request.user.has_perm("parking.add_parkingspace"):
            return ["parking/parking_fig_manager.html"]
        return ["parking/parking_fig.html"]

    def get(self, request, *args, **kwargs):
        local_now = localtime(timezone.now())
        year = kwargs.get("year") or request.GET.get("year", local_now.year)
        month = kwargs.get("month") or request.GET.get("month", local_now.month)

        # フォールバック処理を含むデータ取得
        qs, self.year, self.month = get_parking_diagram_data(year, month)

        if not qs.exists():
            messages.info(request, "駐車場データが存在しません")
            return redirect("register:facility")

        self.object_list = qs
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        for item in self.object_list:
            context[f"sect{item.no}"] = item

        _, empty_num = ParkingSpace.objects.get_empty_space(self.year, self.month, "")
        num = ParkingSpace.objects.get_parking_space_num(self.year, self.month, "")

        context.update(
            {
                "form": ParkingSpaceFigForm(initial={"year": self.year, "month": self.month}),
                "title": f"{self.year}年{self.month}月度の状況：空き＝{empty_num}台/{num}台",
            }
        )
        return context


class UtilizationRateView(LoginRequiredMixin, TemplateView):
    """稼働率の表示"""

    template_name = "parking/utilization_rate.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        local_now = localtime(timezone.now())
        year = self.request.GET.get("year", local_now.year)
        month = self.request.GET.get("month", local_now.month)

        metrics, has_data = get_utilization_metrics(year, month)

        context.update(
            {
                "form": ParkingSpaceListForm(initial={"year": year, "month": month}),
                "title": f"{year}年 {month}月 稼働率",
                **metrics,  # plain, machine_up, machine_down, utilization_rate が展開される
            }
        )
        return context


# 追加分


class ParkingSpaceManagementView(PermissionRequiredMixin, ListView):
    """管理者用 リスト表示"""

    model = ParkingSpace
    permission_required = "parking.add_parkingspace"
    raise_exception = True

    def get_template_names(self):
        # モバイル判定がある場合も共通のテンプレートを返す（元のロジックを維持）
        return ["parking/management.html"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        local_now = localtime(timezone.now())
        year = self.request.GET.get("year", local_now.year)
        month = self.request.GET.get("month", local_now.month)
        parking_type = self.request.GET.get("parking_type")

        # 一般用と共通のService関数を利用
        qs, total = get_parking_summary(year, month, parking_type)

        context.update(
            {
                "parking_list": qs,
                "total": total,
                "form": ParkingSpaceListForm(
                    initial={"year": year, "month": month, "parking_type": parking_type}
                ),
                "title": f"{year}-{month}-01",
            }
        )
        return context


class IncomeRirekiView(LoginRequiredMixin, ListView):
    """駐車場収入履歴一覧"""

    model = ParkingSpace
    template_name = "parking/income_history.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        local_now = localtime(timezone.now())
        year = self.request.GET.get("year", local_now.year)

        # Service層で履歴と集計を取得
        qs, total, noincome = get_income_history_metrics(year)

        context.update(
            {
                "parking": qs,
                "total": total,
                "noincome": noincome,
                "form": IncomeHistoryForm(initial={"year": year}),
            }
        )
        return context
