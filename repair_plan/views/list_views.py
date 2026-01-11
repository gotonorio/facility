from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import ListView
from repair_plan.forms import RepairPlanListForm
from repair_plan.models import KoujiName
from repair_plan.services.list_service import (
    get_koujitype_aggregation,
    get_repair_plan_summary,
    get_version_and_manager_info,
    get_yearly_repair_summary,
)


class RepairPlanListView(LoginRequiredMixin, ListView):
    """長期修繕計画を表示"""

    model = KoujiName
    template_name = "repair_plan/repairplan_list.html"
    context_object_name = "repairplan_list"

    def get_form_kwargs(self):
        """Formに渡す引数の辞書を作成
        - ListViewにはget_form_kwargs関数が無いため、自分で作成する。
        """
        # Formクラスの __init__ に渡したい値を辞書にまとめる
        kwargs = {
            "initial": {"koujitype": self.koujitype_param},
            "is_manager": self.is_manager,
            "ver": self.version_obj,
        }
        # もしこれが FormView や CreateView なら super().get_form_kwargs() を
        # 混ぜますが、ListViewの場合はこの辞書だけでOKです
        return kwargs

    def get_queryset(self):
        """Service層を呼び出し、メインのリストを返す"""
        # 1. パラメータ取得
        ver_param = self.kwargs.get("version") or self.request.GET.get("version")
        self.koujitype_param = self.kwargs.get("kouji_type") or self.request.GET.get("koujitype") or "ALL"

        # 2. Service呼び出し
        self.version_obj, self.is_manager = get_version_and_manager_info(self.request.user, ver_param)

        # Serviceからリストと合計を取得。合計は get_context_data で使うため保持しておく
        repair_plan_qs, self.total_amount = get_repair_plan_summary(self.version_obj, self.koujitype_param)

        return repair_plan_qs

    def get_context_data(self, **kwargs):
        """リスト以外の付加情報（合計、フォーム、設定値）をセット"""
        context = super().get_context_data(**kwargs)

        # get_form_kwargs() を呼び出して、アンパックしてFormに渡す
        form_kwargs = self.get_form_kwargs()
        context["form"] = RepairPlanListForm(**form_kwargs)

        # get_querysetで取得・保持した変数を利用
        context.update(
            {
                "total": self.total_amount,
                "start_year": -settings.INITIAL_YEAR,
                "version_no": self.version_obj,
            }
        )
        return context


class RepairPlanByYearView(PermissionRequiredMixin, ListView):
    """シミュレーションにおいて年度を指定して長期修繕計画を表示"""

    model = KoujiName  # 主となるモデルを明示
    template_name = "repair_plan/repairplan_by_year.html"
    permission_required = "repair_plan.add_koujiname"
    context_object_name = "repairplan_by_year"  # テンプレートでの変数名を固定

    def get_queryset(self):
        # 1. パラメータ取得
        ver_param = self.kwargs.get("ver") or self.request.GET.get("ver")
        year_param = self.kwargs.get("year") or self.request.GET.get("year")

        # 2. Service呼び出し
        self.repair_plan, self.total = get_yearly_repair_summary(
            ver_param,
            year_param,
        )

        return self.repair_plan

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update(
            {
                "total": self.total,
                "start_year": -settings.INITIAL_YEAR,
            }
        )
        return context


class RepairPlanByKoujitypeView(PermissionRequiredMixin, ListView):
    """工事種別ごとに集計表示"""

    model = KoujiName  # 主となるモデルを明示
    template_name = "repair_plan/repairplan_by_koujitype.html"
    permission_required = "repair_plan.add_koujiname"
    context_object_name = "repairplan_by_koujitype"  # テンプレートでの変数名を固定

    def get_form_kwargs(self):
        """Formに渡す引数の辞書を作成
        - ListViewにはget_form_kwargs関数が無いため、自分で作成する。
        """
        # Formクラスの __init__ に渡したい値を辞書にまとめる
        kwargs = {
            "is_manager": self.is_manager,
            "ver": self.version_obj,
        }
        # もしこれが FormView や CreateView なら super().get_form_kwargs() を
        # 混ぜますが、ListViewの場合はこの辞書だけでOKです
        return kwargs

    def get_queryset(self):
        # 1. バージョンの決定（URL引数 or クエリパラメータ or 最新)
        ver_param = self.kwargs.get("version") or self.request.GET.get("version")

        # Service層で適切なバージョンオブジェクトと権限を取得
        self.version_obj, self.is_manager = get_version_and_manager_info(self.request.user, ver_param)

        # 2. 集計データの取得
        # ここで取得した self.total は get_context_data で使いたいのでインスタンス変数に保持
        qs, self.total_amount = get_koujitype_aggregation(self.version_obj)

        return qs  # ← データを返すことで context_object_name にセットされる

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # get_form_kwargs() を呼び出して、アンパックしてFormに渡す
        form_kwargs = self.get_form_kwargs()
        context["form"] = RepairPlanListForm(**form_kwargs)

        context.update(
            {
                "total": self.total_amount,
                "ver": self.version_obj,
                "start_year": -settings.INITIAL_YEAR,
            }
        )
        return context


class RepairPlanUpdateListView(RepairPlanListView):
    """長期修繕計画の編集用list表示
    - ToDo
    - templateファイルで管理者の場合、「編集・削除」ボタンを表示するようにすれば、
        わざわざ編集用のVieteファイルを表示するだけのviewクラスを作成する必要はない。どちらがスマートか？
    """

    def get_template_names(self):
        # モバイル判定ロジック（将来の拡張用）
        return ["repair_plan/repairplan_update_list.html"]
