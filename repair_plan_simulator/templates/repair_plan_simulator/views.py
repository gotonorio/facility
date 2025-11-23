import logging

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import get_object_or_404, redirect, reverse
from django.views.generic import CreateView, FormView, TemplateView, UpdateView
from plan.lib import utils
from plan.models import KoujiName, MasterPlan
from plan.views.data_views import RepairPlanUpdateListView

from repair_plan_simulator.forms import CPICreateForm, ShuuzenhiIncomeCreateForm, SimulateDataForm
from repair_plan_simulator.lib import simulator
from repair_plan_simulator.models import ConsumerPriceIndex, Shuuzenhi_income

logger = logging.getLogger(__name__)


# ----------------------------------------------------------------------------
# シミュレーション計算
# ----------------------------------------------------------------------------
class SimulateView(LoginRequiredMixin, FormView):
    """シミュレーション計算
    - 未施工の計画工事金額を年度毎に集計。
    - 消費税、経費を考慮。
    - 計画初年度の修繕会計残高から実施済み工事金額を減額した形でシミュレーションを行う。
    """

    template_name = "repair_plan_simulator/simulate_pc.html"
    form_class = SimulateDataForm
    # 初期画面表示
    only_manager = False

    def get_form_kwargs(self):
        """FormViewでform_classの__init__()へ引数を渡す
        - FormViewの画面表示で最初に呼ばれるため、ここでグループを判断する。
        """
        kwargs = super(SimulateView, self).get_form_kwargs()
        # 閲覧権限の取得
        _, self.only_manager = utils.get_latest_version(self.request.user)
        kwargs["only_manager"] = self.only_manager
        return kwargs

    def get_template_names(self):
        """templateファイルを切り替える"""
        if self.request.user_agent_flag == "mobile":
            template_name = "repair_plan_simulator/simulate_pc.html"
            # template_name = "repair_plan_simulator/simulate_mobile.html"
        else:
            template_name = "repair_plan_simulator/simulate_pc.html"
        return [template_name]

    def get_context_data(self, **kwargs):
        """get_form_kwargs()が呼ばれた後に呼ばれる
        ModelChoiceField は、モデルの主キー（id）を value に使う。
        そのため任意のvalue値を使いたい時は、idでvalueを取得する処理が必要。
        """
        context = super().get_context_data(**kwargs)
        # idとvalueが不一致の場合の処理
        ver = False
        ver_id = self.request.GET.get("keikaku_ver", False)
        if ver_id:
            plan = MasterPlan.objects.get(version=int(ver_id))
            ver = plan.version

        # シミュレーション画面が表示された時は計算処理しない。（実行ボタンが押された場合に計算を行う）
        if ver:
            sim_data = {}
            # 経費率
            expense_rate = float(self.request.GET.get("expense_rate"))
            # 消費税率
            sales_tax_rate = float(self.request.GET.get("sales_tax_rate"))
            # 修繕積立金の収入率
            shuuzenhi_rate = float(self.request.GET.get("shuuzenhi_rate"))
            # 駐車場料金の修繕会計への振替金額率（全額の場合は1.0となる）
            parking_rate = float(self.request.GET.get("parking_rate"))
            # 物価指数
            cpi_flg = self.request.GET.get("cpi_flg")
            # form
            sim_data["ver"] = ver
            sim_data["expense_rate"] = expense_rate
            sim_data["sales_tax_rate"] = sales_tax_rate
            sim_data["shuuzenhi_rate"] = shuuzenhi_rate
            sim_data["parking_rate"] = parking_rate
            sim_data["cpi_flg"] = cpi_flg
            form = SimulateDataForm(
                # SimulateDataFormの__init__()でonly_managerを受け取れるようにする。
                self.only_manager,
                initial={
                    "keikaku_ver": ver_id,
                    "expense_rate": sim_data["expense_rate"],
                    "sales_tax_rate": sim_data["sales_tax_rate"],
                    "shuuzenhi_rate": sim_data["shuuzenhi_rate"],
                    "parking_rate": sim_data["parking_rate"],
                    "cpi_flg": sim_data["cpi_flg"],
                },
            )

            # 長期修繕計画の年度集計した支出リスト
            expense = simulator.calc_expense_list(ver, expense_rate, sales_tax_rate, cpi_flg)
            # 計画初年度の修繕会計残高を読み込む。
            qs_dev = MasterPlan.objects.filter(version=ver).values("balance")
            balance = qs_dev[0]["balance"]
            # 修繕会計の収入を追加
            simulate_data = simulator.add_income_list(expense, sim_data, balance)
            # シミュレーションで除外（do_calc=False）工事の一覧表示データ
            excluded_data = KoujiName.objects.filter(version__version=ver, do_calc=False).order_by(
                "kouji_year"
            )
            # contextに追加
            context["simulate_data"] = simulate_data
            context["form"] = form
            context["excluded_data"] = excluded_data
            context["start_year"] = -settings.INITIAL_YEAR
            # 指定された年の修繕計画を表示するため、versionをcontextに追加しておく
            context["version"] = ver
        return context


# ----------------------------------------------------------------------------
# シミュレーション計算用の収入データ作成処理
# ----------------------------------------------------------------------------
class CreateIncomeView(PermissionRequiredMixin, CreateView):
    """計画初年度からの実収入を登録"""

    model = Shuuzenhi_income
    form_class = ShuuzenhiIncomeCreateForm
    template_name = "repair_plan_simulator/income_form.html"
    # 必要な権限（管理者権限）
    permission_required = "plan.add_koujiname"
    # 権限がない場合、Forbidden 403を返す。これがない場合はログイン画面に飛ばす。
    raise_exception = True

    # 保存が成功した場合に遷移するurl
    def get_success_url(self):
        return reverse("repair_plan_simulator:create_income")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["masterlist"] = Shuuzenhi_income.objects.all().order_by("-year")
        return context


# ----------------------------------------------------------------------------
# シミュレーション計算用の収入データ修正処理
# ----------------------------------------------------------------------------
class UpdateIncomeView(PermissionRequiredMixin, UpdateView):
    """計画初年度からの実収入を修正する"""

    model = Shuuzenhi_income
    form_class = ShuuzenhiIncomeCreateForm
    template_name = "repair_plan_simulator/income_form.html"
    # 必要な権限（管理者権限）
    permission_required = "plan.add_koujiname"
    # 権限がない場合、Forbidden 403を返す。これがない場合はログイン画面に飛ばす。
    raise_exception = True

    # 保存が成功した場合に遷移するurl
    def get_success_url(self):
        return reverse("repair_plan_simulator:create_income")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["masterlist"] = Shuuzenhi_income.objects.all().order_by("-year")
        return context


# ----------------------------------------------------------------------------
# シミュレーション計算用の収入データ一覧表示
# ----------------------------------------------------------------------------
class SimulateDataView(LoginRequiredMixin, TemplateView):
    """シミュレーションの基礎データ一覧"""

    template_name = "repair_plan_simulator/simulate_data.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["master_data"] = MasterPlan.objects.all().order_by("-version")
        context["income_data"] = Shuuzenhi_income.objects.all().order_by("-year")
        context["cpi_data"] = ConsumerPriceIndex.objects.order_by("year")

        return context


# ----------------------------------------------------------------------------
# シミュレーション計算時に除外する工事データ一覧表示
# ----------------------------------------------------------------------------
class SimulatePlanListView(UpdateRepairPlanListView):
    """シミュレーション時に除外工事を設定するためのView"""

    template_name = "repair_plan_simulator/except_list.html"


def reset_do_calc(request, pk):
    """KoujiNameモデルのdo_calcをリセット（オンに）する
    予定工事を除外してシミュレーションする時にdo_calcを0にセットする。
    これをリセットするためだけの関数。
    """
    # 更新対象のモデルインスタンスを取得
    instance = get_object_or_404(KoujiName, pk=pk)
    # do_calcを1にセットする。
    instance.do_calc = 1
    # インスタンスを保存
    instance.save()

    # シミュレーション画面へリダイレクト。
    return redirect("repair_plan_simulator:do_simulate")


def unset_do_calc(request, pk):
    """KoujiNameモデルのdo_calcをオフにする"""
    # 更新対象のモデルインスタンスを取得
    instance = get_object_or_404(KoujiName, pk=pk)
    # do_calcを0にセットする。
    instance.do_calc = 0
    # インスタンスを保存
    instance.save()

    # シミュレーション画面へリダイレクト。
    return redirect("repair_plan_simulator:do_simulate")


# ----------------------------------------------------------------------------
# シミュレーション計算時の物価指数データの作成処理
# ----------------------------------------------------------------------------
class CreateCPIView(PermissionRequiredMixin, CreateView):
    """物価指数を登録"""

    model = ConsumerPriceIndex
    form_class = CPICreateForm
    template_name = "repair_plan_simulator/cpi_form.html"
    # 必要な権限（管理者権限）
    permission_required = "plan.add_koujiname"
    # 権限がない場合、Forbidden 403を返す。これがない場合はログイン画面に飛ばす。
    raise_exception = True

    # 保存が成功した場合に遷移するurl
    def get_success_url(self):
        return reverse("repair_plan_simulator:create_cpi")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cpi_list"] = ConsumerPriceIndex.objects.all().order_by("year")
        return context


# ----------------------------------------------------------------------------
# シミュレーション計算時の物価指数データのUPDATE処理
# ----------------------------------------------------------------------------
class UpdateCPIView(PermissionRequiredMixin, UpdateView):
    """物価指数を修正する"""

    model = ConsumerPriceIndex
    form_class = CPICreateForm
    template_name = "repair_plan_simulator/cpi_form.html"
    # 必要な権限（管理者権限）
    permission_required = "plan.add_koujiname"
    # 権限がない場合、Forbidden 403を返す。これがない場合はログイン画面に飛ばす。
    raise_exception = True

    # 保存が成功した場合に遷移するurl
    def get_success_url(self):
        return reverse("repair_plan_simulator:create_cpi")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cpi_list"] = ConsumerPriceIndex.objects.all().order_by("year")
        return context

    def form_valid(self, form):
        """連続した物価上昇率をセット・保存する"""
        continuas = form.cleaned_data["continuas"]
        if continuas:
            # 自分で保存処理をする。
            this_year = form.cleaned_data["year"]
            cpi = form.cleaned_data["cpi"]
            comment = form.cleaned_data["comment"]
            last_year = ConsumerPriceIndex.get_lastyear()["last_year"]
            err_list = ConsumerPriceIndex.save_continuas_cpi(this_year, last_year, cpi, comment)
            logger.debug(err_list)
        else:
            # 親クラスのform_valid(form)で保存処理する。
            super().form_valid(form)
        return redirect(self.get_success_url())
