# repair_plan_simulator/views/simulate_views.py
# -----------------------------------------------------------------------------
# シミュレーション実行画面
# -----------------------------------------------------------------------------

import datetime
import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import FormView
from facility.services import get_latest_version
from repair_plan.models import MasterPlan

from repair_plan_simulator.forms import SimulateDataForm
from repair_plan_simulator.services import calc_expense, calc_income, matplotlib_service

logger = logging.getLogger(__name__)


class SimulateView(LoginRequiredMixin, FormView):
    """シミュレーション実行画面"""

    template_name = "repair_plan_simulator/simulate_pc.html"
    form_class = SimulateDataForm

    def get_form_kwargs(self):
        """TemplateView以外でFormに渡す引数を追加"""
        kwargs = super().get_form_kwargs()
        _, self.is_manager = get_latest_version(self.request.user)
        kwargs["is_manager"] = self.is_manager
        return kwargs

    def get_template_names(self):
        if self.request.user_agent_flag == "mobile":
            return ["repair_plan_simulator/simulate_pc.html"]
        return ["repair_plan_simulator/simulate_pc.html"]

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

        if not hasattr(self, "is_manager"):
            _, self.is_manager = get_latest_version(self.request.user)

        # ここでis_managerをコンテキストにセットする。
        context["is_manager"] = self.is_manager

        # 1. GETパラメータの取得をクリーンに
        ver_str = self.request.GET.get("masterplan_ver")
        export_requested = self.request.GET.get("export") == "true"

        if not ver_str:
            return context

        # 2. シミュレーションに必要な設定を整理
        sim_params = {
            "expense_rate": float(self.request.GET.get("expense_rate", 0)),
            "sales_tax_rate": float(self.request.GET.get("sales_tax_rate", 0)),
            "shuuzenhi_rate": float(self.request.GET.get("shuuzenhi_rate", 0)),
            "parking_rate": float(self.request.GET.get("parking_rate", 0)),
            "cpi_flg": self.request.GET.get("cpi_flg"),
            "include_actual_cost": self.request.GET.get("include_actual_cost"),
        }

        # 3. 計算実行
        simulate_data = self.get_simulation_results(ver_str, sim_params)

        # 4. グラフ生成（必要な時だけ呼び出す）
        if export_requested:
            self.handle_graph_export(simulate_data)

        # 5. コンテキストへのセット
        context.update(
            {
                "simulate_data": simulate_data,
                "version": ver_str,
                "form": SimulateDataForm(initial={"masterplan_ver": ver_str, **sim_params}),
                # ...その他
            }
        )

        return context

    def handle_graph_export(self, simulate_data):
        """グラフ生成とメッセージ処理を担当"""

        # # 西暦を取得（例: 2026）
        # current_year = datetime.datetime.now().strftime("%Y")
        # filename = f"simulate_graph_{current_year}.png"

        # sophiagardes.orgで配信するため、常に最新のグラフを同じ名前で保存する
        filename = "simulate_graph_latest.png"

        graph_data = [[r["kouji_year"], r["income_ruikei"], r["ruikei_cost"]] for r in simulate_data]

        # ファイル保存実行
        success = matplotlib_service.generate_and_save_chart(graph_data, filename)

        if success:
            messages.success(self.request, f"{current_year}年度版のグラフを更新・保存しました。")
        else:
            messages.error(self.request, "グラフの保存に失敗しました。")

        # if matplotlib_service.generate_and_save_chart(graph_data, filename):
        #     messages.success(self.request, "長期修繕計画のグラフを保存しました")
        # else:
        #     messages.error(self.request, "出力に失敗しました")
