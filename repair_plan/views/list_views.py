import logging

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import F, IntegerField
from django.db.models.aggregates import Sum
from django.views import generic
from facility.services import get_latest_version
from repair_plan.forms import RepairPlanListForm
from repair_plan.models import KoujiName, MasterPlan

logger = logging.getLogger(__name__)


class RepairPlanListView(LoginRequiredMixin, generic.TemplateView):
    """長期修繕計画を表示
    長期修繕計画はversionにより複数を登録できるようにしているため、ListViewは
    使わずTemplateViewを継承して処理する。
    """

    def get_template_names(self):
        """templateファイルをuser agentで切り替える"""
        if self.request.user_agent_flag == "mobile":
            template_name = "repair_plan/repairplan_pc.html"
            # template_name = "repair_plan/repairplan_mobile.html"
        else:
            template_name = "repair_plan/repairplan_pc.html"
        return [template_name]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 値が''の場合は、そのまま''が設定されてしまう。
        if kwargs:
            # ビューが渡す場合、URLから渡されたpkなどはkwargsでデータが渡される。
            ver = str(kwargs.get("version"))
            koujitype = str(kwargs.get("kouji_type"))
        else:
            # formから渡された場合、GETパラメータで取得する。
            ver = self.request.GET.get("version", False)
            koujitype = self.request.GET.get("koujitype", False)

        # 修繕計画のバージョンとユーザの管理者権限
        latest_version, is_manager = get_latest_version(self.request.user)
        # バージョン選択の処理
        if ver is False or ver is None:
            ver = latest_version

        # 工事種類の選択処理
        if koujitype is False or koujitype == "" or koujitype is None:
            koujitype = "ALL"

        # クエリの作成（verはMasterPlanのversion番号）)
        repair_plan = KoujiName.objects.get_koujiname_list(ver, koujitype).order_by(
            "kouji_year", "kouji_type"
        )
        # 合計金額を計算する。
        total = 0.0
        for item in repair_plan:
            total = total + (item.unit_price * item.kouji_quantity)

        # TemplateViewでformに初期値を渡す。verはRepairPlanListFormの__init__で処理する。
        form = RepairPlanListForm(is_manager, ver, initial={"koujitype": koujitype})

        # contextの設定
        context["repairplan_list"] = repair_plan
        context["form"] = form
        context["start_year"] = -settings.INITIAL_YEAR
        context["total"] = int(total)
        return context


class RepairPlanByYearView(PermissionRequiredMixin, generic.TemplateView):
    """年度を指定して長期修繕計画を表示"""

    model = KoujiName
    template_name = "repair_plan/repairplan_by_year.html"
    permission_required = "repair_plan.add_koujiname"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ver = self.kwargs.get("ver", False)
        year = self.kwargs.get("year", False)

        # 工事選択
        repair_plan = KoujiName.objects.get_repair_plan_list_by_year(ver, year).order_by(
            "kouji_type", "kouji_name"
        )
        if not repair_plan:
            # 修繕計画がない場合は、空のリストを返す。
            repair_plan = []

        # 合計金額を計算する。
        total = 0.0
        for item in repair_plan:
            # if item.complete:
            #     continue
            total = total + (item.unit_price * item.kouji_quantity)

        context["repairplan_by_year"] = repair_plan
        context["start_year"] = -settings.INITIAL_YEAR
        context["total"] = int(total)
        return context


class RepairPlanByKoujitypeView(PermissionRequiredMixin, generic.TemplateView):
    """長期修繕計画を工事種別表示
    長期修繕計画はversionにより複数を登録できるようにしているため、ListViewは
    使わずTemplateViewを継承して処理する。
    """

    model = KoujiName
    template_name = "repair_plan/repairplan_by_koujitype.html"
    permission_required = "repair_plan.add_koujiname"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 値が''の場合は、そのまま''が設定されてしまう。
        ver = self.request.GET.get("version", False)

        # 修繕計画のバージョンとユーザの管理者権限
        latest_version, is_manager = get_latest_version(self.request.user)
        # バージョン選択の処理
        if ver is False:
            ver = latest_version

        # https://stackoverflow.com/questions/38546108/django-aggregation-expression-contains-mixed-types-you-must-set-output-field
        # https://docs.djangoproject.com/en/2.2/ref/models/expressions/
        # select_related()とkouji_type__master_nameでリレーション先データを得る。
        qs = (
            KoujiName.objects.get_koujiname_list(ver, "ALL")
            .values("kouji_type__master_name")
            .annotate(subtotal=Sum(F("kouji_quantity") * F("unit_price"), output_field=IntegerField()))
            .order_by("kouji_type")
        )
        # 合計金額を計算する。
        total = 0.0
        for item in qs:
            total = total + item["subtotal"]

        # forms.pyのKeikakuListFormに初期値を設定する．http://i2bskn.hateblo.jp/entry/20120826/1345936779
        form = RepairPlanListForm(is_manager, ver, initial={"version": ver})
        context["ver"] = ver
        context["repairplan_by_koujitype"] = qs
        context["form"] = form
        context["start_year"] = -settings.INITIAL_YEAR
        context["total"] = int(total)
        return context


class MasterPlanListView(LoginRequiredMixin, generic.TemplateView):
    """長期修繕計画マスタの一覧表示"""

    model = MasterPlan
    template_name = "repair_plan/masterplan_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 修繕計画のバージョンとユーザの管理者権限
        _, is_manager = get_latest_version(self.request.user)

        # 管理者のみ全データ
        if is_manager:
            qs = MasterPlan.objects.all().order_by("-version")
        else:
            qs = MasterPlan.objects.filter(only_manager=is_manager).order_by("-version")

        context["masterlist"] = qs
        return context
