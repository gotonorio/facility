import csv
import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Max, Q
from django.http import Http404, HttpResponse
from django.shortcuts import redirect
from django.utils import timezone
from django.utils.timezone import localtime
from django.views.generic import ListView, TemplateView
from facility.forms import IncomeHistoryForm
from parking.forms import ParkingSpaceFigForm, ParkingSpaceListForm
from parking.models import ParkingSpace, ParkingType

logger = logging.getLogger(__name__)
User = get_user_model()


class ParkingSpaceListView(LoginRequiredMixin, ListView):
    """一般ユーザ用 駐車場リスト表示"""

    model = ParkingSpace
    template_name = "parking/parkingspace_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        local_now = localtime(timezone.now())
        year = str(self.request.GET.get("year", local_now.year))
        month = str(self.request.GET.get("month", local_now.month))
        # 使用中駐車場
        qs = ParkingSpace.objects.get_parking_space(year, month, "").order_by("no")
        # 駐車場使用料の合計を計算
        total = 0
        for d in qs:
            if d.status_of_use == "使用中" or d.status_of_use == "解約予定":
                total += d.parking_type.rent_fee
        # form既定値
        form = ParkingSpaceListForm(
            initial={
                "year": year,
                "month": month,
            }
        )
        context["total"] = total
        context["form"] = form
        context["title"] = f"{year}年 {month}月"
        # 1画面表示
        space1, space2, space3 = make_parking_list(qs)
        context["space1"] = space1
        context["space2"] = space2
        context["space3"] = space3
        return context


class ParkingSpaceManagementView(PermissionRequiredMixin, ListView):
    """管理者用 リスト表示"""

    model = ParkingSpace
    # template_name = 'parking/management_list.html'
    # 必要な権限
    permission_required = "parking.add_parkingspace"
    # 権限がない場合、Forbidden 403を返す。
    raise_exception = True

    def get_template_names(self):
        """templateファイルを切り替える"""
        if self.request.user_agent_flag == "mobile":
            template_name = "parking/management.html"
            # template_name = "parking/mobile/management_mobile.html"
        else:
            template_name = "parking/management.html"
        return [template_name]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        local_now = localtime(timezone.now())
        year = str(self.request.GET.get("year", local_now.year))
        month = str(self.request.GET.get("month", local_now.month))
        parking_type = self.request.GET.get("parking_type")

        qs = ParkingSpace.objects.get_parking_space(year, month, parking_type).order_by("no")
        # 駐車場使用料の合計を計算
        total = 0
        for d in qs:
            if d.status_of_use == "使用中" or d.status_of_use == "解約予定":
                total += d.parking_type.rent_fee
        # form既定値
        form = ParkingSpaceListForm(initial={"year": year, "month": month, "parking_type": parking_type})
        context["parking_list"] = qs
        context["total"] = total
        context["form"] = form
        # context['title'] = f'{year}年{month}月'
        context["title"] = f"{year}-{month}-01"

        return context


class IncomeRirekiView(LoginRequiredMixin, ListView):
    """駐車場収入履歴一覧"""

    model = ParkingSpace
    template_name = "parking/income_history.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        local_now = localtime(timezone.now())
        year = str(self.request.GET.get("year", local_now.year))
        qs = ParkingSpace.objects.get_parking_rireki(year)
        # 駐車場使用料の合計を計算
        total = 0
        noincome = 0
        for d in qs:
            total += d["income"]
            noincome += d["noincome"]
        # form既定値
        form = IncomeHistoryForm(
            initial={
                "year": year,
            }
        )
        context["parking"] = qs.order_by("-payment_date")
        context["form"] = form
        context["total"] = total
        context["noincome"] = noincome
        return context


@permission_required("parking.add_parkingspace")
def export_parkingfee(request, year):
    """駐車場使用料データをCSV出力"""
    fn = f"parkingfee{year}.csv"
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = "attachment; filename=" + fn
    # HttpResponseオブジェクトはファイルっぽいオブジェクトなので、csv.writerにそのまま渡せる。
    writer = csv.writer(response)
    # 駐車場使用料一覧を抽出。
    qs = (
        ParkingSpace.objects.filter(Q(status_of_use="使用中") | Q(status_of_use="解約予定"))
        .filter(payment_date=year)
        .order_by("room_number")
    )
    # 1行目に年月日を出力。2行目からcsvデータ。
    writer.writerow(
        [
            year,
        ]
    )
    for data in qs:
        writer.writerow([data.room_number, data.parking_type.rent_fee])
    return response


def make_parking_list(qs):
    """parking spaceのqsを「平置き1」「機械式」「平置き2」に分ける"""
    space1 = []
    space2 = []
    space3 = []
    for space in qs:
        data = []
        data.append(space.no)
        data.append(space.parking_type)
        data.append(space.status_of_use)
        data.append(space.parking_type.rent_fee)
        if space.no < 43:
            space1.append(data)
        elif space.no < 87:
            space2.append(data)
        else:
            space3.append(data)
    return space1, space2, space3


class ParkingFigView(LoginRequiredMixin, ListView):
    """空き駐車場の表示"""

    model = ParkingSpace
    context_object_name = "parkings"

    def get_template_names(self):
        """管理者templateファイルを切り替える"""
        try:
            user = User.objects.get(username=self.request.user)
            if user.has_perm("parking.add_parkingspace"):
                return ["parking/parking_fig_manager.html"]
            else:
                return ["parking/parking_fig.html"]
        except ObjectDoesNotExist:
            return ["parking/parking_fig.html"]

    def get(self, request, *args, **kwargs):
        """get_context_data()の前に呼ばれる
        ここで、yearとmonthを取得して、object_listにセットする。
        kwargsがある場合は、kwargsから取得する。
        ない場合は、GETパラメータから取得する。
        get_context_data()ではredirectできないため、get()でredirectする。
        """
        local_now = localtime(timezone.now())

        # 年月の取得（kwargs優先）
        if kwargs:
            self.year = str(kwargs.get("year"))
            self.month = str(kwargs.get("month"))
        else:
            self.year = str(request.GET.get("year", local_now.year))
            self.month = str(request.GET.get("month", local_now.month))

        qs = ParkingSpace.objects.get_parking_space(self.year, self.month, "").order_by("no")

        # データが存在しない場合
        if not qs.exists():
            latest_date = ParkingSpace.objects.aggregate(Max("payment_date"))["payment_date__max"]
            if latest_date:
                self.year = latest_date.year
                self.month = latest_date.month
                qs = ParkingSpace.objects.get_parking_space(self.year, self.month, "").order_by("no")
            else:
                messages.info(request, "駐車場データが存在しません")
                return redirect("register:facility")

        # queryset を保持
        self.object_list = qs
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        """qsをtemplateに直接渡す必要がないので不要だが、参考のために残す
        - get() 内でセットされた object_list を使う
        """
        return getattr(self, "object_list", ParkingSpace.objects.none())

    def get_context_data(self, **kwargs):
        """templateにデータを渡すために必要なデータをセットする"""
        context = super().get_context_data(**kwargs)

        # 駐車場ごとのセクションデータ
        for item in self.object_list:
            context[f"sect{item.no}"] = item

        # form初期値
        form = ParkingSpaceFigForm(
            initial={
                "year": self.year,
                "month": self.month,
            }
        )

        # 空き駐車場数
        _, empty_num = ParkingSpace.objects.get_empty_space(self.year, self.month, "")
        # 利用可能駐車場数
        num = ParkingSpace.objects.get_parking_space_num(self.year, self.month, "")

        context["form"] = form
        context["title"] = f"{self.year}年{self.month}月度の駐車場状況：空き＝{empty_num}台/{num}台"
        return context


class UtilizationRateView(LoginRequiredMixin, TemplateView):
    """稼働率の表示"""

    def get_template_names(self):
        """templateファイルを切り替える"""
        if self.request.user_agent_flag == "mobile":
            template_name = "parking/utilization_rate.html"
        else:
            template_name = "parking/utilization_rate.html"
        return [template_name]

    def get_context_data(self, **kwargs):
        """データが無い月が選択された場合の処理を追加する"""
        context = super().get_context_data(**kwargs)
        local_now = localtime(timezone.now())
        year = str(self.request.GET.get("year", local_now.year))
        month = str(self.request.GET.get("month", local_now.month))

        # form既定値
        form = ParkingSpaceListForm(
            initial={
                "year": year,
                "month": month,
            }
        )
        # 稼働率
        # [1]:区画数　[2]:空き区画数　[3]:利用数　[4]:稼働率
        plain = [settings.PLAIN_PARKING, 0, 0, 0, 0]
        machine_up = [settings.MACHINE_UP_PARKING, 0, 0, 0, 0]
        machine_down = [settings.MACHINE_DOWN_PARKING, 0, 0, 0, 0]

        # 平面駐車場
        try:
            ptype = ParkingType.objects.get(parking_type=settings.PLAIN_PARKING)
        except ParkingType.DoesNotExist:
            raise Http404("駐車場稼働率で駐車場タイプの取得に失敗しました。管理者に連絡してください。")

        plain[1] = ParkingSpace.objects.get_parking_space_num(year, month, ptype)
        # この年月のデータが存在しなければ、デフォルト値で処理する。
        if plain[1] < 1:
            context["plain"] = plain
            context["machine_up"] = machine_up
            context["machine_down"] = machine_down
            context["form"] = form
            context["title"] = f"{year}年 {month}月 稼働率"
            return context
        _, plain[2] = ParkingSpace.objects.get_empty_space(year, month, ptype)
        plain[3] = plain[1] - plain[2]
        plain[4] = int((plain[1] - plain[2]) * 100 / plain[1])
        # 機械式上段
        ptype = ParkingType.objects.get(parking_type=settings.MACHINE_UP_PARKING)
        machine_up[1] = ParkingSpace.objects.get_parking_space_num(year, month, ptype)
        _, machine_up[2] = ParkingSpace.objects.get_empty_space(year, month, ptype)
        machine_up[3] = machine_up[1] - machine_up[2]
        machine_up[4] = int((1 - machine_up[2] / machine_up[1]) * 100)
        # 機械式下段
        ptype = ParkingType.objects.get(parking_type=settings.MACHINE_DOWN_PARKING)
        machine_down[1] = ParkingSpace.objects.get_parking_space_num(year, month, ptype)
        _, machine_down[2] = ParkingSpace.objects.get_empty_space(year, month, ptype)
        # 利用数
        machine_down[3] = machine_down[1] - machine_down[2]
        # 稼働率
        machine_down[4] = int((1 - (machine_down[2]) / machine_down[1]) * 100)
        # 駐車場全体
        utilization_rate = (plain[3] + machine_up[3] + machine_down[3]) / (
            plain[1] + machine_up[1] + machine_down[1]
        )

        context["plain"] = plain
        context["machine_up"] = machine_up
        context["machine_down"] = machine_down
        context["utilization_rate"] = int(utilization_rate * 100)
        context["form"] = form
        context["title"] = f"{year}年 {month}月 稼働率"
        return context
