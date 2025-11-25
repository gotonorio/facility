import logging

from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views import generic

# from repair_plan_simulator.models import Shuuzenhi_income
from repair_plan.forms import RepairPlanTableForm
from repair_plan.lib import utils
from repair_plan.models import KoujiName

logger = logging.getLogger(__name__)


class RepairPlanTableView(PermissionRequiredMixin, generic.TemplateView):
    """長期修繕計画表（詳細版）"""

    model = KoujiName
    template_name = "repair_plan/repairplan_table.html"
    permission_required = "repair_plan.add_koujiname"

    def repairplan_table(self, ver, start_year, end_year):
        # 長期修繕計画表を抽出する（listとする）
        qs_list = KoujiName.objects.get_repair_plan_list(ver, start_year, end_year, False)
        # 年毎の支出合計を保持するListの初期化
        year_total = [0 for i in range(start_year, end_year + 3)]
        # 合計
        all_total = 0
        # 年毎の支出合計を計算
        for year in qs_list:
            for i in range(2, len(year_total)):
                year_total[i] += year[i]
        # 計画期間の支出合計
        for i in range(2, len(year_total)):
            all_total += year_total[i]

        return qs_list, year_total, all_total

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ver = self.request.GET.get("version", False)

        # 修繕計画のバージョンとユーザの管理者権限
        latest_version, is_manager = utils.get_latest_version(self.request.user)

        # formに初期値を設定する
        form = RepairPlanTableForm(
            is_manager,
            initial={
                "version": ver,
            },
        )
        # バージョンが選択されていない場合は、フォームのみ表示して終了
        if not ver:
            context["form"] = form
            return context

        #
        # 修繕計画の開始年と終了年
        #
        start_year = KoujiName.objects.get_year_range(ver)["start_year"]
        end_year = KoujiName.objects.get_year_range(ver)["end_year"]
        # データ不足の場合（バージョンデータのみで計画データがないケース）
        if (start_year is None) or (end_year is None):
            # messages.info(self.request, f"ver={ver}の長期修繕計画データが存在しません。")
            context["form"] = form
            return context

        #
        # 計画修繕支出テーブルの生成
        #
        qs_list, year_total, all_total = self.repairplan_table(ver, start_year, end_year)

        # 年毎の支出合計
        context["total"] = year_total
        # 支出合計
        context["all_total"] = all_total

        # タイトル（西暦）Listを作成
        context["year"] = [i for i in range(start_year, end_year + 1)]
        # 修繕計画表
        context["repairplan_list"] = list(qs_list)
        context["form"] = form

        # #
        # # 修繕積立金収入
        # #
        # list_size = end_year - start_year + 3
        # income_qs = Shuuzenhi_income.objects.filter(real=True).order_by("year")
        # income_last = income_qs.last()
        # # 定義されている最新の修繕積立金の収入リス
        # shuuzenhi_incomelist = [income_last.income] * list_size
        # shuuzenhi_incomelist[0:2] = [0, 0]
        # # 想定する駐車場会計からの繰入れ収入
        # parking_incomelist = [income_last.parking_income] * list_size
        # # 想定するその他（駐輪場、バイク置き場等）からの繰入れ収入
        # extra_incomelist = [income_last.extra_income] * list_size
        # # 収入合計
        # income_total = [
        #     x + y + z
        #     for x, y, z in zip(
        #         shuuzenhi_incomelist, parking_incomelist, extra_incomelist
        #     )
        # ]

        # # 修繕積立金収入
        # context["shuuzenhi_income"] = shuuzenhi_incomelist
        # # 駐車場収入
        # context["parking_income"] = parking_incomelist
        # # 駐輪場・バイク置場等収入
        # context["extra_income"] = extra_incomelist
        # # 収入合計
        # context["income_total"] = income_total
        return context


class RepairPlanSimpleTableView(RepairPlanTableView):
    """長期修繕計画表（シンプル版）"""

    model = KoujiName
    template_name = "repair_plan/repairplan_simpletable.html"
    permission_required = "repair_plan.view_koujiname"

    def repairplan_table(self, ver, start_year, end_year):
        # 長期修繕計画表を抽出する（listとする）
        qs_list = KoujiName.objects.get_repair_plan_list(ver, start_year, end_year, True)
        # 年毎の支出合計を保持するListの初期化
        year_total = [0 for i in range(start_year, end_year + 3)]
        # 合計
        all_total = 0
        # 年毎の支出合計を計算
        for year in qs_list:
            for i in range(1, len(year_total)):
                year_total[i] += year[i]
        # 計画期間の支出合計
        for i in range(1, len(year_total) - 1):
            all_total += year_total[i]

        return qs_list, year_total, all_total
