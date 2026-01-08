from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views import generic
from facility.services import get_latest_version
from repair_plan.forms import RepairPlanListForm
from repair_plan.services.table_service import get_repair_plan_table_data


class RepairPlanTableView(PermissionRequiredMixin, generic.TemplateView):
    """長期修繕計画表（詳細版）"""

    template_name = "repair_plan/repairplan_table.html"
    permission_required = "repair_plan.add_koujiname"
    is_simple = False  # 子クラスで上書き

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # バージョンの決定
        ver = self.kwargs.get("version") or self.request.GET.get("version")
        latest_version, is_manager = get_latest_version(self.request.user)
        ver = ver or latest_version

        # Formの作成
        form = RepairPlanListForm(is_manager, ver, initial={"version": ver})
        context["form"] = form

        if not ver:
            return context

        # Service層で複雑な計算を実行
        data = get_repair_plan_table_data(ver, is_simple=self.is_simple)

        if data:
            context.update(
                {
                    "repairplan_list": data["repairplan_list"],
                    "total": data["year_total"],
                    "all_total": data["all_total"],
                    "year": data["years"],
                }
            )

        return context


class RepairPlanSimpleTableView(RepairPlanTableView):
    """長期修繕計画表（シンプル版）"""

    template_name = "repair_plan/repairplan_simpletable.html"
    permission_required = "repair_plan.view_koujiname"
    is_simple = True  # ロジックを切り替え


# import logging

# from django.contrib.auth.mixins import PermissionRequiredMixin
# from django.views import generic
# from facility.services import get_latest_version

# # from repair_plan_simulator.models import Shuuzenhi_income
# from repair_plan.forms import RepairPlanListForm
# from repair_plan.models import KoujiName

# logger = logging.getLogger(__name__)


# class RepairPlanTableView(PermissionRequiredMixin, generic.TemplateView):
#     """長期修繕計画表（詳細版）"""

#     model = KoujiName
#     template_name = "repair_plan/repairplan_table.html"
#     permission_required = "repair_plan.add_koujiname"

#     def repairplan_table(self, ver, start_year, end_year):
#         # 長期修繕計画表を抽出する（listとする）
#         qs_list = KoujiName.objects.get_repair_plan_list(ver, start_year, end_year, False)
#         # 年毎の支出合計を保持するListの初期化
#         year_total = [0 for i in range(start_year, end_year + 3)]
#         # 合計
#         all_total = 0
#         # 年毎の支出合計を計算
#         for year in qs_list:
#             for i in range(2, len(year_total)):
#                 year_total[i] += year[i]
#         # 計画期間の支出合計
#         for i in range(2, len(year_total)):
#             all_total += year_total[i]

#         return qs_list, year_total, all_total

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         # update後にget_success_url()で遷移する場合、kwargsにデータが渡される。typeはint)
#         if kwargs:
#             ver = str(kwargs.get("version"))
#         else:
#             ver = self.request.GET.get("version", False)

#         # 修繕計画のバージョンとユーザの管理者権限
#         latest_version, is_manager = get_latest_version(self.request.user)

#         # バージョン選択の処理
#         if ver is False or ver is None:
#             ver = latest_version

#         # formに初期値を設定する（同時にTemplateViewdではここでis_managerを渡す）
#         form = RepairPlanListForm(
#             is_manager,
#             ver,
#             initial={
#                 "version": ver,
#             },
#         )
#         # バージョンが選択されていない場合は、フォームのみ表示して終了
#         if not ver:
#             context["form"] = form
#             return context

#         #
#         # 修繕計画の開始年と終了年
#         #
#         start_year = KoujiName.objects.get_year_range(ver)["start_year"]
#         end_year = KoujiName.objects.get_year_range(ver)["end_year"]
#         # データ不足の場合（バージョンデータのみで計画データがないケース）
#         if (start_year is None) or (end_year is None):
#             # messages.info(self.request, f"ver={ver}の長期修繕計画データが存在しません。")
#             context["form"] = form
#             return context

#         #
#         # 計画修繕支出テーブルの生成
#         #
#         qs_list, year_total, all_total = self.repairplan_table(ver, start_year, end_year)

#         # 年毎の支出合計
#         context["total"] = year_total
#         # 支出合計
#         context["all_total"] = all_total

#         # タイトル（西暦）Listを作成
#         context["year"] = [i for i in range(start_year, end_year + 1)]
#         # 修繕計画表
#         context["repairplan_list"] = list(qs_list)
#         context["form"] = form

#         return context


# class RepairPlanSimpleTableView(RepairPlanTableView):
#     """長期修繕計画表（シンプル版）"""

#     model = KoujiName
#     template_name = "repair_plan/repairplan_simpletable.html"
#     permission_required = "repair_plan.view_koujiname"

#     def repairplan_table(self, ver, start_year, end_year):
#         # 長期修繕計画表を抽出する（listとする）
#         qs_list = KoujiName.objects.get_repair_plan_list(ver, start_year, end_year, True)
#         # 年毎の支出合計を保持するListの初期化
#         year_total = [0 for i in range(start_year, end_year + 3)]
#         # 合計
#         all_total = 0
#         # 年毎の支出合計を計算
#         for year in qs_list:
#             for i in range(1, len(year_total)):
#                 year_total[i] += year[i]
#         # 計画期間の支出合計
#         for i in range(1, len(year_total) - 1):
#             all_total += year_total[i]

#         return qs_list, year_total, all_total
