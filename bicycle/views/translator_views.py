import logging

from bicycle.models import BicycleSpace
from common.forms.translator_forms import KuraselTranslatorForm
from common.services.translator_service import execute_translator
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.timezone import localtime
from django.views.generic import FormView

logger = logging.getLogger(__name__)


class BicycleContractImportView(PermissionRequiredMixin, FormView):
    template_name = "common/translator_form.html"
    form_class = KuraselTranslatorForm
    permission_required = "parking.add_parkingspace"
    success_url = reverse_lazy("bicycle:list")

    def get_initial(self):
        # GETパラメータからの年月取得をここに集約
        now = localtime(timezone.now())
        return {
            "year": self.request.GET.get("year", now.year),
            "month": self.request.GET.get("month", now.month),
        }

    def form_valid(self, form):
        # クラセルの共用設備データ取込み（Service関数の実行）
        rtn, result_ctx = execute_translator(form.cleaned_data)

        if rtn:
            # ここでは result_ctx が辞書であることが確定するので警告も出ません
            year = result_ctx["year"]
            month = result_ctx["month"]
            chk_kind = result_ctx["chk_kind"]
        else:
            # 失敗した時の処理（メッセージを表示するなど）
            messages.error(self.request, result_ctx["error_message"])
            return self.render_to_response(self.get_context_data(form=form, **result_ctx))

        if not chk_kind:
            messages.error(self.request, "共用設備区分を確認してください。")
            return self.render_to_response(self.get_context_data(form=form, **result_ctx))

        # 自転車置場データ（区画番号、部屋番号、使用状況）の取込み
        b_list = BicycleSpace.objects.get_bicycle_space(year, month, "").values_list(
            "no", "room_number", "status_of_use"
        )
        qs_data = list(b_list)
        result_ctx["bicycle_list"] = qs_data

        # チェック
        chk_list = []
        for row, row_qs in zip(result_ctx["data_list"], qs_data):
            if row[4] == "契約中" and (row_qs[2] not in ("使用中", "解約予定")):
                chk_list.append(row)

        result_ctx["check_list"] = chk_list
        if chk_list == []:
            messages.info(self.request, "クラセルとの誤差はありません。")

        return self.render_to_response(self.get_context_data(form=form, **result_ctx))
