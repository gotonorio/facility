import datetime
import logging

from bicycle.forms import BicycleUpdateForm, MonthlyProcessingForm
from bicycle.models import BicycleSpace
from dateutil.relativedelta import relativedelta
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import Count
from django.shortcuts import redirect, reverse
from django.urls import reverse_lazy
from django.views.generic import FormView, UpdateView
from facility.services import select_period

logger = logging.getLogger(__name__)


class BicycleSpaceUpdateView(PermissionRequiredMixin, UpdateView):
    """駐輪場データのUPDATE"""

    model = BicycleSpace
    form_class = BicycleUpdateForm
    template_name = "bicycle/update_form.html"
    # 必要な権限（データ登録できる権限は共通）
    permission_required = "parking.add_parkingspace"
    # 権限がない場合、Forbidden 403を返す。これがない場合はログイン画面に飛ばす。
    raise_exception = True
    # 保存が成功した場合に遷移するurl
    success_url = reverse_lazy("bicycle:list")

    def get_success_url(self):
        """更新後にリダイレクトするURLを動的に決定
        - BicycleSpaceListView()ではself.kwargsでyearとmonthを受け取れる。
        """
        year = self.object.date.year
        month = self.object.date.month
        return reverse("bicycle:list", kwargs={"year": year, "month": month})

    def form_valid(self, form):
        """部屋番号を0にし忘れることがあるので、チェックする"""
        # commitを停止する。
        self.object = form.save(commit=False)
        no = form.cleaned_data["no"]
        room = form.cleaned_data["room_number"]
        status = form.cleaned_data["status_of_use"]
        if room == 0 and status != "空き":
            messages.info(
                self.request,
                f"駐輪場 No.{no}の部屋番号が「0」なら使用状況は「空き」にしてください。",
            )
            # 元のformに戻してエラーメッセージを表示させる。
            return redirect("bicycle:update", self.kwargs["pk"])
        elif status == "空き" and room > 0:
            messages.info(
                self.request,
                f"駐輪場 No.{no}の使用状況が「空き」なら部屋番号は「0」にしてください。",
            )
            # 元のformに戻してエラーメッセージを表示させる。
            return redirect("bicycle:update", self.kwargs["pk"])
        else:
            # データを保存。
            self.object.save()
            # 親のform_validに戻ると保存処理されてしまうので抜けて戻る。
            return redirect(self.get_success_url())


class MonthlyProcessingView(PermissionRequiredMixin, FormView):
    """月次処理"""

    template_name = "bicycle/monthly_processing.html"
    form_class = MonthlyProcessingForm
    # 必要な権限
    permission_required = "parking.add_parkingspace"
    # 権限がない場合、Forbidden 403を返す。
    raise_exception = True
    success_url = reverse_lazy("bicycle:list")

    def latest_data(self):
        """駐輪場データから使用中の最新日付（dict）を返す"""
        qs = BicycleSpace.objects.values("date").filter(status_of_use="使用中")
        qs = qs.distinct().order_by("-date")
        latest_date = qs.first()
        return latest_date

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        year = self.request.POST.get("year", False)
        month = self.request.POST.get("month", False)
        # formフィールドに初期値を設定。
        yymm = self.latest_data()
        next_yymm = yymm["date"] + relativedelta(months=1)
        if not year:
            year = next_yymm.year
        if not month:
            month = next_yymm.month
        # formフィールドに初期値を設定。
        monthly_form = MonthlyProcessingForm(
            initial={
                "year": year,
                "month": month,
            }
        )
        # 登録済みデータ
        qs = BicycleSpace.objects.values("date")
        qs = qs.annotate(count=Count("date")).filter(status_of_use="空き")
        qs = qs.order_by("-date")
        context["list"] = qs
        context["form"] = monthly_form
        return context

    def post(self, request, *args, **kwargs):
        """最新の駐車場データで指定年月のデータを一括生成する"""
        year = self.request.POST.get("year", False)
        month = self.request.POST.get("month", False)
        # 指定年月のデータが存在しなければ処理を行う。
        new_date = datetime.date(int(year), int(month), 1)
        qs = BicycleSpace.objects.all().filter(date=new_date)
        if len(qs) < 1:
            # 最新の駐車場データ
            latest_date = self.latest_data()["date"]
            # 抽出期間
            tstart, tend = select_period(latest_date.year, latest_date.month)
            qs = BicycleSpace.objects.all().filter(date__range=[tstart, tend]).order_by("no")
            new_parking = []
            for d in qs:
                parking = BicycleSpace(
                    no=d.no,
                    location=d.location,
                    room_number=d.room_number,
                    date=new_date,
                    status_of_use=d.status_of_use,
                    comment=d.comment,
                )
                new_parking.append(parking)
            BicycleSpace.objects.bulk_create(new_parking)
        else:
            messages.info(self.request, f"駐輪場の{new_date}は既に存在しています。")
        return redirect(self.get_success_url())
