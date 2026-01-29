from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.utils.timezone import localtime
from django.views.generic import TemplateView

from common.forms.base_form import YearMonthForm
from motorcycle.models import MotorCycleSpace
from motorcycle.services.display_service import get_motorcycle_summary


class MotorCycleSpaceListView(LoginRequiredMixin, TemplateView):
    """バイク駐車場一覧"""

    model = MotorCycleSpace

    def get_template_names(self):
        """デバイスに応じてテンプレートを切り替える（将来的な拡張性を維持）"""
        if self.request.user_agent_flag == "mobile":
            template_name = "motorcycle/motorcycle_list.html"
        else:
            template_name = "motorcycle/motorcycle_list.html"
        return [template_name]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 1. 年月の正規化ロジック
        local_now = localtime(timezone.now())
        year = str(
            self.kwargs.get("year") or self.request.GET.get("year", local_now.year)
        )
        month = str(
            self.kwargs.get("month") or self.request.GET.get("month", local_now.month)
        )

        # 2. Service層を利用したデータ取得
        summary_data = get_motorcycle_summary(year, month)

        # 3. コンテキストの更新
        context.update(
            {
                "form": YearMonthForm(initial={"year": year, "month": month}),
                "title": f"{year}年 {month}月",
                **summary_data,  # motorcycle_list, count_all, count_use が展開される
            }
        )

        return context
