import logging
import os

from common.forms.base_form import YearMonthForm
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.timezone import localtime
from django.views.generic import DetailView, ListView, TemplateView, View
from parking.forms import ParkingSpaceFigForm
from parking.models import ParkingSpace
from parking.services.display_service import (
    categorize_parking_spaces,
    get_income_history_metrics,
    get_parking_diagram_data,
    get_parking_summary,
    get_utilization_metrics,
    resolve_year_month,
)

logger = logging.getLogger(__name__)


class ParkingSpaceListView(PermissionRequiredMixin, ListView):
    """一般ユーザ用 駐車場リスト表示"""

    model = ParkingSpace
    template_name = "parking/parking_list.html"
    permission_required = "repair_plan.view_koujiname"
    context_object_name = "parking_list"

    def get_queryset(self):
        # パラメータの確定
        self.year, self.month = resolve_year_month(
            self.kwargs.get("year"),
            self.kwargs.get("month"),
            self.request.GET.get("year"),
            self.request.GET.get("month"),
        )

        # メインデータを取得してself に保持する（Service層を利用）
        qs, self.total = get_parking_summary(self.year, self.month)
        return qs

    # テンプレートで使う「辞書」の作成（Dictを返す）
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 取得済みの qs は get_queryset で context["parking_list"] に入っている
        space1, space2, space3 = categorize_parking_spaces(context["parking_list"])

        context.update(
            {
                "total": self.total,
                "form": YearMonthForm(initial={"year": self.year, "month": self.month}),
                "title": f"{self.year}年 {self.month}月",
                "space1": space1,
                "space2": space2,
                "space3": space3,
            }
        )
        return context


class ParkingSpaceManagementView(PermissionRequiredMixin, ListView):
    """管理者の編集用 リスト表示"""

    model = ParkingSpace
    permission_required = "parking.add_parkingspace"
    raise_exception = True
    context_object_name = "parking_list"

    def get_template_names(self):
        # モバイル判定がある場合も共通のテンプレートを返す（元のロジックを維持）
        return ["parking/management.html"]

    # データの取得（HttpResponseを返す）
    def get_queryset(self):
        # パラメータの確定
        self.year, self.month = resolve_year_month(
            self.kwargs.get("year"),
            self.kwargs.get("month"),
            self.request.GET.get("year"),
            self.request.GET.get("month"),
        )

        # 2. メインデータを取得してself に保持する（Service層を利用）
        qs, self.total = get_parking_summary(self.year, self.month)

        return qs

    # テンプレートで使う「辞書」の作成（Dictを返す）
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update(
            {
                # "parking_list": self.qs,
                "total": self.total,
                "form": YearMonthForm(initial={"year": self.year, "month": self.month}),
                "title": f"{self.year}-{self.month}-01",
            }
        )
        return context


class ParkingFigView(PermissionRequiredMixin, TemplateView):
    """空き駐車場の図解表示"""

    model = ParkingSpace
    context_object_name = "parkings"
    permission_required = "repair_plan.view_koujiname"

    def get_template_names(self):
        if self.request.user.has_perm("parking.add_parkingspace"):
            return ["parking/parking_fig_manager.html"]
        elif self.request.user.has_perm("parking.view_parkingspace"):
            return ["parking/parking_fig_director.html"]
        return ["parking/parking_fig.html"]

    # get() はレスポンス制御とデータの取得を行う。
    def get(self, request, *args, **kwargs):
        year, month = resolve_year_month(
            self.kwargs.get("year"),
            self.kwargs.get("month"),
            self.request.GET.get("year"),
            self.request.GET.get("month"),
        )
        self.qs, self.year, self.month = get_parking_diagram_data(year, month)

        # querysetエラー処理でredirectするのはget()で行う。
        if not self.qs.exists():
            messages.info(request, "駐車場データが存在しません")
            return redirect("register:facility")

        return super().get(request, *args, **kwargs)

    # get_context_data()はテンプレートで使う「辞書」の作成だけとする。（Dictを返す）
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 駐車場区画番号をキーとしたcontextデータの展開
        for item in self.qs:
            context[f"sect{item.no}"] = item

        _, empty_num = ParkingSpace.objects.get_empty_space(self.year, self.month, "")
        num = ParkingSpace.objects.get_parking_space_num(self.year, self.month, "")

        context.update(
            {
                "form": ParkingSpaceFigForm(initial={"year": self.year, "month": self.month}),
                "title": f"{self.year}年{self.month}月度の駐車場：空き＝{empty_num}台/{num}台",
            }
        )
        # htmlファイル出力は、当年月データまたは最新のデータを出力する。
        context["year"] = self.year
        context["month"] = self.month

        return context


class ParkingFigExportView(PermissionRequiredMixin, View):
    """駐車場図のHTML出力専用View"""

    # facility_manager以上が処理可能
    permission_required = "parking.add_parkingspace"

    def get(self, request, *args, **kwargs):
        # 年月決定
        year, month = resolve_year_month(
            kwargs.get("year"),
            kwargs.get("month"),
            request.GET.get("year"),
            request.GET.get("month"),
        )

        # データ取得
        qs, year, month = get_parking_diagram_data(year, month)

        if not qs.exists():
            messages.info(request, "駐車場データが存在しません")
            return redirect("register:facility")

        # 表示Viewと同じロジックでデータ構築
        context = {}

        for item in qs:
            context[f"sect{item.no}"] = item

        _, empty_num = ParkingSpace.objects.get_empty_space(year, month, "")
        num = ParkingSpace.objects.get_parking_space_num(year, month, "")

        context.update(
            {
                "year": year,
                "month": month,
                "empty_num": empty_num,
                "num": num,
                "title": f"{year}年{month}月度の駐車場：空き＝{empty_num}台/{num}台",
            }
        )

        # HTML生成
        is_ok = _generate_parking_maps_html(context)

        if is_ok:
            messages.success(request, f"{year}年{month}月の駐車場状況図を保存しました")
        else:
            messages.error(request, f"{year}年{month}月の駐車場状況図の出力に失敗しました")

        # 元の表示画面へ戻す
        return redirect("parking:fig", year=year, month=month)


class UtilizationRateView(PermissionRequiredMixin, TemplateView):
    """稼働率の表示"""

    template_name = "parking/utilization_rate.html"
    permission_required = "repair_plan.view_koujiname"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        local_now = localtime(timezone.now())
        year = self.request.GET.get("year", local_now.year)
        month = self.request.GET.get("month", local_now.month)

        metrics, has_data = get_utilization_metrics(year, month)

        context.update(
            {
                "form": YearMonthForm(initial={"year": year, "month": month}),
                "title": f"{year}年 {month}月 稼働率",
                **metrics,  # plain, machine_up, machine_down, utilization_rate が展開される
            }
        )
        return context


class IncomeRirekiView(PermissionRequiredMixin, ListView):
    """駐車場収入履歴一覧"""

    model = ParkingSpace
    template_name = "parking/income_history.html"
    permission_required = "repair_plan.view_koujiname"

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
                "form": YearMonthForm(initial={"year": year}),
            }
        )
        return context


def _generate_parking_maps_html(context_data):
    """駐車場図のHTMLを生成して共有領域に保存する関数"""
    try:
        # 1. HTMLを生成
        html_string = render_to_string("parking/parking_fig_output.html", context_data)

        # 2. 保存先のフルパスを作成
        filename = "parking_fig_latest.html"
        file_path = os.path.join(settings.HTML_OUTPUT_ROOT, filename)

        # 共有領域ディレクトリが存在しない場合の処理
        os.makedirs(settings.HTML_OUTPUT_ROOT, exist_ok=True)

        # 3. 書き出し
        # 書き込みそのものが失敗した場合、ここで例外（Error）が発生する
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html_string)

        # すべて成功したらパスを返す
        return file_path

    except (OSError, IOError) as e:
        # 権限エラー(PermissionError)やディスクフル、パス間違いなどはここでキャッチ
        logger.error(f"HTMLファイルの書き出しに失敗しました: {e}")
        return False

    except Exception as e:
        # それ以外の予期せぬエラー（テンプレートエラーなど）をキャッチ
        logger.error(f"予期せぬエラーが発生しました: {e}")
        return False


class ParkingDetailView(PermissionRequiredMixin, DetailView):
    """directorグループ用の詳細表示View"""

    model = ParkingSpace
    template_name = "parking/parking_fig_detail.html"
    permission_required = "parking.view_parkingspace"
    # logger.debug(object.no)
