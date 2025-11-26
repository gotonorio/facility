import datetime
import logging

from dateutil.relativedelta import relativedelta
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import Count, Q
from django.shortcuts import redirect, reverse
from django.urls import reverse_lazy
from django.views.generic import FormView, UpdateView
from parking.forms import MonthlyProcessingForm, ParkingUpdateForm
from parking.models import ParkingSpace

logger = logging.getLogger(__name__)


def get_parkingspace():
    """月毎の空き駐車場数を返す 予約中は空きとカウントする"""
    qs = ParkingSpace.objects.values("payment_date")
    qs = qs.annotate(count=Count("payment_date")).filter(Q(status_of_use="空き") | Q(status_of_use="予約中"))
    # qs = qs.annotate(count=Count('payment_date')).filter(status_of_use='空き')
    qs = qs.order_by("-payment_date")
    return qs


class MonthlyProcessingView(PermissionRequiredMixin, FormView):
    """月次処理"""

    template_name = "parking/monthly_processing.html"
    form_class = MonthlyProcessingForm
    # 必要な権限
    permission_required = "parking.add_parkingspace"
    # 権限がない場合、Forbidden 403を返す。
    raise_exception = True
    success_url = reverse_lazy("parking:management")

    def latest_data(self):
        """駐車場データから使用中または解約予定の最新日付を返す"""
        qs = ParkingSpace.objects.values("payment_date").filter(
            Q(status_of_use="使用中") | Q(status_of_use="解約予定")
        )
        qs = qs.distinct().order_by("-payment_date")
        latest_date = qs.first()
        return latest_date

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        year = self.request.POST.get("year", False)
        month = self.request.POST.get("month", False)
        # formフィールドに初期値を設定。
        yymm = self.latest_data()
        next_yymm = yymm["payment_date"] + relativedelta(months=1)
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
        context["list"] = get_parkingspace()
        context["form"] = monthly_form
        return context

    def post(self, request, *args, **kwargs):
        """最新の駐車場データで指定年月のデータを一括生成する"""
        year = self.request.POST.get("year", False)
        month = self.request.POST.get("month", False)
        # 指定年月のデータが存在しなければ処理を行う。
        new_date = datetime.date(int(year), int(month), 1)
        qs = ParkingSpace.objects.all().filter(payment_date=new_date)
        if len(qs) < 1:
            # 最新の駐車場データ
            latest_date = self.latest_data()
            qs = ParkingSpace.objects.all().filter(payment_date=latest_date["payment_date"]).order_by("no")
            new_parking = []
            for d in qs:
                parking = ParkingSpace(
                    no=d.no,
                    parking_type=d.parking_type,
                    name=d.name,
                    room_number=d.room_number,
                    payment_date=new_date,
                    comment=d.comment,
                    status_of_use=d.status_of_use,
                )
                new_parking.append(parking)
            ParkingSpace.objects.bulk_create(new_parking)
        else:
            messages.info(self.request, f"{new_date}は既に存在しています。")
        # return super(MonthlyProcessingView, self).post(request, *args, **kwargs)
        return redirect(self.get_success_url())


class ParkingUpdateView(PermissionRequiredMixin, UpdateView):
    """駐車場データのUPDATE"""

    model = ParkingSpace
    form_class = ParkingUpdateForm
    template_name = "parking/update_form.html"
    # 必要な権限（データ登録できる権限は共通）
    permission_required = "parking.add_parkingspace"
    # 権限がない場合、Forbidden 403を返す。これがない場合はログイン画面に飛ばす。
    raise_exception = True

    def get_success_url(self):
        """更新後にリダイレクトするURLを動的に決定
        - ParkingFigView()ではself.kwargsでyearとmonthを受け取れる。
        """
        year = self.object.payment_date.year
        month = self.object.payment_date.month
        return reverse("parking:fig", kwargs={"year": year, "month": month})

    def form_valid(self, form):
        """部屋番号を0にし忘れることがあるので、チェックする"""
        # commitを停止する。
        self.object = form.save(commit=False)
        no = form.cleaned_data["no"]
        room = form.cleaned_data["room_number"]
        status = form.cleaned_data["status_of_use"]
        if room == 0 and status != "空き" and status != "使用中止":
            messages.info(self.request, f"駐車場 No.{no}の部屋番号を入力してください。")
            # 元のformに戻してエラーメッセージを表示させる。
            return redirect("parking:update", self.kwargs["pk"])
        elif status == "空き" and room > 0:
            messages.info(
                self.request, f"駐車場 No.{no}の使用状況が「空き」なら部屋番号は「0」にしてください。"
            )
            # 元のformに戻してエラーメッセージを表示させる。
            return redirect("parking:update", self.kwargs["pk"])
        else:
            # データを保存して状況図に戻る。
            self.object.save()
            return redirect(self.get_success_url())
