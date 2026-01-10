# ----------------------------------------------------------------------------
# Name: cycledata_actions.py
# Purpose: 長期修繕計画サイクルデータ関連のアクションビュー
# ----------------------------------------------------------------------------

import logging

from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import generic
from repair_plan_cycle.form import CycleDataDuplicateForm
from repair_plan_cycle.models import KoujiCycleData

logger = logging.getLogger(__name__)


class CycleDataDuplicateView(PermissionRequiredMixin, generic.FormView):
    """周期データをバージョンを指定して丸ごと複製するビュー"""

    form_class = CycleDataDuplicateForm
    template_name = "repair_plan_cycle/duplicate_form.html"
    success_url = reverse_lazy("repair_plan_cycle:cycledata_list")
    permission_required = "repair_plan.add_koujiname"

    def get_context_data(self, **kwargs):
        """コンテキストデータにタイトルとマスタプランリストを追加
        - formは自動で追加される。
        - formだけならgetメソッドをオーバーライドしても良いが、今回はcontext_dataにまとめて追加する。
            def get(self, request, *args, **kwargs):
                form = self.form_class()
                return render(request, self.template_name, {"form": form})
        """
        context = super().get_context_data(**kwargs)
        context["title"] = "工事周期データの複製作成"
        context["masterlist"] = KoujiCycleData.objects.all().order_by("-version")
        context["masterlist"] = KoujiCycleData.objects.values("version").distinct().order_by("-version")
        return context

    def post(self, request, *args, **kwargs):
        form = CycleDataDuplicateForm(request.POST)
        if not form.is_valid():
            return render(request, self.template_name, {"form": form})

        source_version = int(form.cleaned_data["source_version"])
        new_version = int(form.cleaned_data["new_version"])

        # すでに新 version が存在する場合は中止
        if KoujiCycleData.objects.filter(version=new_version).exists():
            messages.error(request, f"Version {new_version} のデータは既に存在します。")
            return render(request, self.template_name, {"form": form})

        # 複製元データの取得
        source_qs = KoujiCycleData.objects.filter(version=source_version)

        if not source_qs.exists():
            messages.error(request, f"複製元 Version {source_version} のデータが見つかりません。")
            return render(request, self.template_name, {"form": form})

        # 複製用リスト
        new_objects = []

        for row in source_qs:
            new_objects.append(
                KoujiCycleData(
                    version=new_version,
                    kouji_type=row.kouji_type,
                    kouji_name=row.kouji_name,
                    first_year=row.first_year,
                    repeat_cycle=row.repeat_cycle,
                    cost=row.cost,
                    comment=row.comment,
                )
            )

        # 一括登録
        KoujiCycleData.objects.bulk_create(new_objects)

        messages.success(request, "工事周期データの複製が完了しました。")
        return redirect(self.get_success_url())
