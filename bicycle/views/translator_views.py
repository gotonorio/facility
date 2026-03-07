import logging

from bicycle.models import BicycleSpace
from common.forms.translator_forms import KuraselTranslatorForm
from common.services.translator_service import execute_translator
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.http import urlencode
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
        result_ctx = execute_translator(form.cleaned_data)

        year = result_ctx["year"]
        month = result_ctx["month"]
        kind = result_ctx["kind"]

        # 自転車置場データの取込み
        b_list = BicycleSpace.objects.get_bicycle_space(year, month, "").values_list(
            "no", "room_number", "status_of_use"
        )
        qs_data = list(b_list)
        result_ctx["bicycle_list"] = qs_data

        # チェック
        chk_list = []
        for i, row in enumerate(result_ctx["data_list"]):
            if row[4] == "契約中" and qs_data[i][2] != "使用中":
                chk_list.append(row)

        result_ctx["difference_list"] = chk_list

        # # 登録成功時の処理
        # msg = f"{year}年{month}月の{kind}データの取り込みが完了しました。"
        # messages.success(self.request, msg)

        return self.render_to_response(self.get_context_data(form=form, **result_ctx))

        # params = urlencode({"year": result["year"], "month": result["month"]})
        # return redirect(f"{reverse('kurasel_translator:create_monthly')}?{params}")
        # return super().form_valid(form)
