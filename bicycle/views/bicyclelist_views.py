import csv
import logging

from bicycle.forms import BicycleSpaseListForm
from bicycle.models import BicycleSpace
from django.conf import settings
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.http import HttpResponse
from django.utils import timezone
from django.utils.timezone import localtime
from django.views.generic import ListView, TemplateView
from facility.forms import IncomeHistoryForm

logger = logging.getLogger(__name__)


def make_bicycle_list(qs):
    """parking spaceのqsを「棟前」「棟東」「棟北」「平置き」に分ける"""
    space1 = []
    space2 = []
    space3 = []
    space4 = []
    for space in qs:
        data = []
        data.append(space.no)
        data.append(space.location)
        data.append(space.status_of_use)
        data.append(space.pk)
        data.append(space.room_number)
        if space.location == "平置き":
            space1.append(data)
        elif space.location == "棟前":
            space2.append(data)
        elif space.location == "棟東":
            space3.append(data)
        elif space.location == "棟北":
            space4.append(data)
        else:
            logger.debug(f"{space.no}の配置データが不明です。")
    return space1, space2, space3, space4


class BicycleSpaceListView(LoginRequiredMixin, TemplateView):
    """駐輪場一覧"""

    model = BicycleSpace
    template_name = "bicycle/bicyclespace_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 年月を正規化
        local_now = localtime(timezone.now())

        if self.kwargs:
            # update後にget_success_url()で遷移するためにkwargsにデータがセットされている。
            year = str(self.kwargs.get("year"))
            month = str(self.kwargs.get("month"))
        else:
            year = str(self.request.GET.get("year", local_now.year))
            month = str(self.request.GET.get("month", local_now.month))

        # forms.pyのKeikakuListFormに初期値を設定する
        form = BicycleSpaseListForm(
            initial={
                "year": year,
                "month": month,
            }
        )
        qs, count_use, qs_type = self.make_query_set(year, month)
        context["bicycle_list"] = qs
        context["form"] = form
        context["total"] = count_use * 200
        context["title"] = f"{year}年 {month}月"
        context["year"] = year
        context["month"] = month
        # 1画面表示用の処理
        if qs_type == "queryset":
            space1, space2, space3, space4 = make_bicycle_list(qs)
            context["space1"] = space1
            context["space2"] = space2
            context["space3"] = space3
            context["space4"] = space4

        return context

    def make_query_set(self, year, month):
        """querysetを生成"""
        qs = BicycleSpace.objects.get_bicycle_space(year, month, "").order_by("no")
        count_use = qs.filter(Q(status_of_use="使用中") | Q(status_of_use="解約予定")).count()
        return qs, count_use, "queryset"


class BicycleSpaceByRoomView(BicycleSpaceListView):
    """住戸別駐輪場一覧
    - BicycleSpaceListVieを継承する。
    """

    template_name = "bicycle/bicyclespace_by_room_pc.html"

    def make_query_set(self, year, month):
        """querysetを生成"""
        # 住戸別駐輪場リスト
        qs = (
            BicycleSpace.get_bicycle_space(year, month, "")
            .exclude(room_number=0)
            .order_by("room_number", "no")
        )
        count_use = qs.filter(status_of_use="使用中").count()
        return qs, count_use, "no"


class BicycleSpaceFeeByRoomView(BicycleSpaceListView):
    """住戸別駐輪場使用料（管理者用）"""

    template_name = "bicycle/bicyclespacefee_by_room_pc.html"

    def make_query_set(self, year, month):
        """querysetを生成"""
        # 住戸別駐輪場リスト
        qs = BicycleSpace.get_bicycle_space(year, month, "").exclude(room_number=0).order_by("room_number")
        qs = qs.values("room_number").annotate(num=Count("no"), fee=Count("no") * settings.BICYCLE_USAGE_FEE)
        count_use = qs.filter(status_of_use="使用中").count()
        return qs, count_use, "dict"


class BicycleIncomeHistoryView(LoginRequiredMixin, ListView):
    """駐輪場収入履歴一覧"""

    model = BicycleSpace
    template_name = "bicycle/bicycleincome_history.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        local_now = localtime(timezone.now())
        year = str(self.request.GET.get("year", local_now.year))
        qs = BicycleSpace.objects.get_bicycle_incomehistory(year)
        # 駐車場使用料の合計を計算
        total = 0
        for d in qs:
            total += d["income"]

        # form既定値
        form = IncomeHistoryForm(
            initial={
                "year": year,
            }
        )
        context["bicycle"] = qs.order_by("-date")
        context["form"] = form
        context["total"] = total
        return context


@permission_required("parking.add_parkingspace")
def export_bicyclefee(request, year, month):
    """駐車場使用料データをCSV出力"""
    fn = f"bicyclefee{year}-{month}.csv"
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = "attachment; filename=" + fn
    # HttpResponseオブジェクトはファイルっぽいオブジェクトなので、csv.writerにそのまま渡せる。
    writer = csv.writer(response)
    qs = BicycleSpace.get_bicycle_space(year, month, "").exclude(room_number=0).order_by("room_number")
    qs = qs.values("room_number").annotate(fee=Count("no") * settings.BICYCLE_USAGE_FEE)
    # 1行目に年月日を出力。2行目からcsvデータ。
    writer.writerow([year, month])
    for data in qs:
        writer.writerow([data["room_number"], data["fee"]])
    return response
