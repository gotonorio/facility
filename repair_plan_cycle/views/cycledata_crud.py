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
        # plan_list = self.create_repair_plan_from_basic_data(
        plan_list = create_repair_plan_from_basic_data(
            data_list=qs_list, start_year=start_year, last_year=last_year + 1
        )
        # (4) 工事の無い年はdummy工事を追加
        # full_plan_list = self.fill_dummydata(plan_list, start_year, last_year)
        full_plan_list = fill_dummydata(plan_list, start_year, last_year)
        # (5) DBに一括登録
        _ = self.save_repair_plan(full_plan_list)
        # return super().form_valid(form)
        return reverse_lazy("repair_plan_cycle:cycledata_list")

    # def create_repair_plan_from_basic_data(self, data_list, start_year, last_year, limmit_num=100):
    #     """
    #     長期修繕計画データを基本データから作成する
    #     - 工事名毎に最大100回分の工事予定を作成.
    #     """
    #     plan_list = []
    #     for row in data_list:
    #         # 最初の工事を行う年（西暦）
    #         yyyy = int(row[3])
    #         # 1つの工事項目についてlimmit_num回繰り返す
    #         for i in range(1, limmit_num):
    #             # 予定年度が最終計画年度以上になったら、次の工事名処理を行う.
    #             if yyyy >= last_year:
    #                 break
    #             else:
    #                 # 工事データをplan_listに追加して、次の工事予定年（西暦）を求める
    #                 yyyy = self.add_planlist(row, yyyy, start_year, plan_list)
    #                 # 周期（row[4]）が0なら1回だけの工事なのでbreakして抜ける
    #                 if int(row[4]) < 1:
    #                     break
    #     return plan_list

    # def add_planlist(self, row, yyyy, start_year, plan_list):
    #     """
    #     修繕計画データリストに追加する処理
    #     """

    #     # rowリストをtmplistにコピー
    #     tmplist = row[:]
    #     # 不要データを削除
    #     del tmplist[3:5]
    #     tmplist.insert(1, yyyy)  # 施工予定年
    #     tmplist.insert(4, 1)  # 数量は「1」に固定
    #     tmplist.insert(5, "式")  # 数量単位は「式」に固定
    #     tmplist.insert(7, 0)  # 実績費用は「0」に固定
    #     # 計画初年度以降のデータをplan_listに追加
    #     if yyyy >= start_year:
    #         plan_list.append(tmplist)
    #     yyyy += int(row[4])

    #     # 次の施工予定年を返す.
    #     return yyyy

    # def fill_dummydata(self, plan_list, start_year, last_year):
    #     """
    #     抜けている年のデータ（ダミーデータ）を追加する
    #     - 長期修繕計画では期間中の工事予定が無い年のデータも必要
    #     """

    #     # 工事予定年だけのリストを作成
    #     year_list = []
    #     for i in plan_list:
    #         year_list.append(i[1])
    #     # 重複年を除去
    #     unique_year_list = list(set(year_list))
    #     # 重複を除去したリストを昇順にソート
    #     unique_year_list.sort()

    #     for cnt_year in range(start_year, last_year):
    #         # データが存在すればスキップする
    #         if cnt_year in unique_year_list:
    #             pass
    #         else:
    #             # 不足している年のダミーデータをplan_listに追加する
    #             dummy_data = [5, 0, "ダミー工事", "ダミー工事", 1, "式", 0, 0, ""]
    #             dummy_data[1] = cnt_year
    #             plan_list.append(dummy_data)
    #         cnt_year += 1

    #     return plan_list

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
