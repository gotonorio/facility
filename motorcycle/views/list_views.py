import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.utils.timezone import localtime
from django.views.generic import TemplateView
from facility.services import select_period
from motorcycle.forms import MotorCycleSpaseListForm
from motorcycle.models import MotorCycleSpace

logger = logging.getLogger(__name__)


class MotorCycleSpaceListView(LoginRequiredMixin, TemplateView):
    """駐輪場一覧"""

    model = MotorCycleSpace

    def get_template_names(self):
        """templateファイルを切り替える"""
        if self.request.user_agent_flag == "mobile":
            template_name = "motorcycle/motorcyclespace_pc.html"
            # template_name = "motorcycle/motorcyclespace_mobile.html"
        else:
            template_name = "motorcycle/motorcyclespace_pc.html"
        return [template_name]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 年月を正規化
        local_now = localtime(timezone.now())

        # reverseでkwargs変数をセットした場合はself.kwargsで受け取る。
        # redirectでkwargs変数をセットした場合はkwargsで受け取る。
        if self.kwargs:
            # update後にget_success_url()で遷移するためにkwargsにデータがセットされている。
            year = str(self.kwargs.get("year"))
            month = str(self.kwargs.get("month"))
        else:
            year = str(self.request.GET.get("year", local_now.year))
            month = str(self.request.GET.get("month", local_now.month))

        # year = str(self.request.GET.get("year", local_now.year))
        # month = str(self.request.GET.get("month", local_now.month))
        # location = str(self.request.GET.get("location"))
        # forms.pyのKeikakuListFormに初期値を設定する
        form = MotorCycleSpaseListForm(
            initial={
                "year": year,
                "month": month,
                # "location": location,
            }
        )
        # 抽出期間
        tstart, tend = select_period(year, month)
        # 区画別駐輪場リスト
        qs = MotorCycleSpace.objects.filter(date__range=[tstart, tend]).order_by("no")
        count_all = qs.count()
        # 駐車場使用料の合計を計算
        count_use = (
            MotorCycleSpace.objects.filter(date__range=[tstart, tend]).filter(status_of_use="使用中").count()
        )
        context["motorcycle_list"] = qs
        context["form"] = form
        context["count_all"] = count_all
        context["count_use"] = count_use
        context["title"] = f"{year}年 {month}月"

        return context
