# repair_plan_simulator/views/simulate_views.py
# -----------------------------------------------------------------------------
# シミュレーション実行画面
# -----------------------------------------------------------------------------

import datetime
import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from facility.services import get_latest_version
from repair_plan.models import MasterPlan

from repair_plan_simulator.forms import SimulateDataForm
from repair_plan_simulator.services import calc_expense, calc_income, matplotlib_service

logger = logging.getLogger(__name__)


class SimulateView(LoginRequiredMixin, ListView):
    """シミュレーション実行メイン画面"""

    model = MasterPlan
    template_name = "repair_plan_simulator/simulate_pc.html"
    form_class = SimulateDataForm
    context_object_name = "master_plans"

    def get_form(self):
        """Formのインスタンス化。GETパラメータを渡すのがポイント"""
        _, self.is_manager = get_latest_version(self.request.user)
        # request.GET にデータがあればバリデーション対象にする
        # ここで渡すis_managerはkwargs変数としてFormクラスの__init__()で受け取れる
        return SimulateDataForm(self.request.GET or None, is_manager=self.is_manager)

    def get_simulation_results(self, ver_str, sim_data):
        """計算実行ロジックをここに集約"""
        plan = MasterPlan.objects.get(version=int(ver_str))
        expense_list = calc_expense.calc_expense_list(
            ver_str,
            sim_data["expense_rate"],
            sim_data["sales_tax_rate"],
            sim_data["cpi_flg"],
            include_actual_cost=sim_data["include_actual_cost"],
        )
        balance = plan.balance
        return calc_income.add_income_list(expense_list, sim_data, balance)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        form = self.get_form()

        # フォームに値が入っていて、バリデーションが通れば計算実行
        if form.is_valid():
            # 型変換済みのデータが手に入る
            sim_data = form.cleaned_data
            ver_val = sim_data["masterplan_ver"]  # ここは Model インスタンス、またはID

            # ver_str として渡す必要がある場合は str(ver_val) などに変換
            simulate_data = self.get_simulation_results(str(ver_val), sim_data)
            context["simulate_data"] = simulate_data
            context["version"] = int(ver_val)

            # グラフ出力が必要な場合
            if self.request.GET.get("export") == "true":
                self.handle_graph_export(simulate_data)

        context["form"] = form
        context["is_manager"] = self.is_manager

        return context

    def handle_graph_export(self, simulate_data):
        """グラフ生成とメッセージ処理を担当"""

        # 西暦を取得（例: 2026）
        current_year = datetime.datetime.now().strftime("%Y")

        # sophiagardes.orgで配信するため、常に最新のグラフを同じ名前で保存する
        filename = "simulate_graph_latest.png"

        graph_data = [[r["kouji_year"], r["income_ruikei"], r["ruikei_cost"]] for r in simulate_data]

        # ファイル保存実行
        success = matplotlib_service.generate_and_save_chart(graph_data, filename, current_year)

        if success:
            messages.success(self.request, f"{current_year}年度版のグラフを更新・保存しました。")
        else:
            messages.error(self.request, "グラフの保存に失敗しました。")
