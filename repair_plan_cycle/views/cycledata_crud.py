# ----------------------------------------------------------------------------
# Name: cycledata_crud.py
# Purpose: 周期データ関連のCRUDビュー
# - 周期データの登録・更新・削除
# - 周期データから長期修繕計画データの作成
# ----------------------------------------------------------------------------

import logging

from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.exceptions import ValidationError
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import generic
from repair_plan.models import KoujiName, MasterKoujiType, MasterPlan, MasterUnit
from repair_plan_cycle.form import (
    CycleDataDeleteForm,
    CycleDataForm,
    RepairPlanCreateForm,
)
from repair_plan_cycle.models import KoujiCycleData
from repair_plan_cycle.services.repairplan_create_service import (
    create_repair_plan_from_basic_data,
    fill_dummydata,
)

logger = logging.getLogger(__name__)


class CycleDataUpdateView(PermissionRequiredMixin, generic.UpdateView):
    """修繕工事の周期データを修正・更新"""

    model = KoujiCycleData
    form_class = CycleDataForm
    # template_name = "koujicycledata_form.html"
    template_name = "repair_plan_cycle/koujicycledata_form.html"
    permission_required = "repair_plan.add_koujiname"

    def get_success_url(self):
        # version_id = self.object.version
        # base_url = reverse_lazy("repair_plan_cycle:")
        # return f"{base_url}?version={version_id}"
        return reverse_lazy("repair_plan_cycle:cycledata_list")


class CycleDataCreateView(PermissionRequiredMixin, generic.CreateView):
    """修繕工事の周期データを新規作成"""

    model = KoujiCycleData
    form_class = CycleDataForm
    # template_name = "koujicycledata_form.html"
    template_name = "repair_plan_cycle/koujicycledata_form.html"
    success_url = reverse_lazy("repair_plan_cycle:")
    permission_required = "repair_plan.add_koujiname"

    def form_valid(self, form):
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["masterlist"] = MasterPlan.objects.all().order_by("-version")
        return context


class RepairplanCreateView(PermissionRequiredMixin, generic.FormView):
    """長期修繕計画データを周期データから新規作成"""

    template_name = "repair_plan_cycle/koujicycledata_form.html"
    form_class = RepairPlanCreateForm
    success_url = reverse_lazy("repair_plan_cycle:")
    permission_required = "repair_plan.add_koujiname"

    def form_valid(self, form):
        version_id = form.cleaned_data["version"]
        start_year = form.cleaned_data["start_year"]
        last_year = form.cleaned_data["last_year"]

        # (1) BasicPlanDataのデータを取得（タプルのリスト）
        qs_basic_plan = KoujiCycleData.objects.filter(version=version_id)
        # (2) 内包処理でリストのリストに変換
        qs_list = [
            list(row)
            for row in qs_basic_plan.values_list(
                "version",
                "kouji_type__master_name",
                "kouji_name",
                "first_year",
                "repeat_cycle",
                "cost",
                "comment",
            )
        ]
        # (3) 長期修繕計画データを作成
        plan_list = create_repair_plan_from_basic_data(
            data_list=qs_list, start_year=start_year, last_year=last_year + 1
        )
        # (4) 工事の無い年はdummy工事を追加
        # full_plan_list = self.fill_dummydata(plan_list, start_year, last_year)
        full_plan_list = fill_dummydata(plan_list, start_year, last_year)
        # (5) DBに一括登録
        _ = self.save_repair_plan(full_plan_list)
        return redirect("repair_plan:repairplan_list")

    def save_repair_plan(self, plan_list):
        """listデータをDBに保存する"""
        # enumerateを使って読み込んだ行番号を取得する。
        for i, row in enumerate(plan_list):
            # (1) 先頭行でMastePlanデータのバージョン番号をチェックする。
            if i == 0:
                try:
                    ver_object = MasterPlan.objects.get(version=row[0])
                except MasterPlan.DoesNotExist:
                    raise ValidationError(
                        f"バージョン番号 {row[0]} は「修繕計画マスタ」に登録されていません!"
                    )
            # (3) 工事種別名のチェック
            try:
                _ = MasterKoujiType.objects.get(master_name=row[2])
            except MasterKoujiType.DoesNotExist:
                raise ValidationError(f"{i + 1}行目の{row[2]} は工事種別マスタが登録されていません!")
            # (4) 施工単位名のチェック
            try:
                _ = MasterUnit.objects.get(unit_name=row[5])
            except MasterUnit.DoesNotExist:
                raise ValidationError(f"{i + 1}行目の{row[5]} は施工単位マスタが登録されていません!")
            # (5) 実支出金額のチェック
            if str(row[7]) == "":
                row[7] = 0

            KoujiName.objects.create(
                version=ver_object,
                kouji_year=row[1],
                kouji_type=MasterKoujiType.objects.get(master_name=row[2]),
                kouji_name=row[3],
                kouji_quantity=row[4],
                unit=MasterUnit.objects.get(unit_name=row[5]),
                unit_price=row[6],
                actual_cost=row[7],
                comment=row[8],
                do_calc=1,
            )


class CycleDataDeleteView(PermissionRequiredMixin, generic.FormView):
    """指定されたversionのKoujiCycleDataを削除する"""

    template_name = "repair_plan_cycle/koujicycledata_delete_form.html"
    form_class = CycleDataDeleteForm
    # 必要な権限（管理者権限）
    permission_required = "repair_plan.add_koujiname"
    success_url = reverse_lazy("repair_plan_cycle:cycledata_list")

    def form_valid(self, form):
        # フォームのデータを処理する
        # このメソッドはPOSTリクエストが有効な場合に呼び出される
        del_version = int(form.cleaned_data["delete_version"])
        yesno = form.cleaned_data["confirm_flg"]
        if yesno:
            del_counts = KoujiCycleData.delete_koujicycledata_by_ver(del_version)
            if del_counts == 0:
                msg = f"version={del_version} のデータは存在しませんでした。"
            else:
                msg = f"version={del_version} のデータを {del_counts} 件削除しました。"
            messages.success(self.request, msg)
        else:
            messages.success(self.request, "削除確認がありません")
        return super().form_valid(form)
