import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import generic

from repair_plan.forms import (
    ImportRepairPlanDataForm,
    MasterKoujiTypeForm,
    MasterUnitForm,
)
from repair_plan.lib import utils
from repair_plan.models import MasterKoujiType, MasterPlan, MasterUnit

logger = logging.getLogger(__name__)


class MasterPlanListView(LoginRequiredMixin, generic.TemplateView):
    """長期修繕計画マスタの一覧表示"""

    model = MasterPlan
    template_name = "plan/masterplan_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 修繕計画のバージョンとユーザの管理者権限
        _, is_manager = utils.get_latest_version(self.request.user)

        # 管理者のみ全データ
        if is_manager:
            qs = MasterPlan.objects.all().order_by("-version")
        else:
            qs = MasterPlan.objects.filter(only_manager=is_manager).order_by("-version")

        context["masterlist"] = qs
        return context


class ImportRepairPlanDataView(PermissionRequiredMixin, generic.FormView):
    """同じversionが存在したら読み込み処理を中止する"""

    template_name = "plan/import_repair_plan.html"
    form_class = ImportRepairPlanDataForm
    success_url = reverse_lazy("repair_plan:repair_plan_list")
    # 必要な権限
    permission_required = "plan.add_koujiname"
    # 権限がない場合、Forbidden 403を返す。これがない場合はログイン画面に飛ばす。
    raise_exception = True

    # バリデーションが通った時に呼ばれる関数を上書きして、save()関数を呼び出す。
    def form_valid(self, form):
        """forms.pyで作成したsave()関数を呼び出して保存する"""
        form.save()
        return redirect("repair_plan:repair_plan_list")


class CreateKoujiTypeView(PermissionRequiredMixin, generic.CreateView):
    """修繕費の工事種別マスターを登録/修正する。
    マスターデータは、数が多くはないので表示しながら入力formを表示させる。
    データが存在すれば表示し、修正か新規登録させる。
    listでページングする場合は https://torina.top/detail/337/#i3 を参照。
    """

    model = MasterKoujiType
    form_class = MasterKoujiTypeForm
    template_name = "plan/master_koujitype_form.html"
    # 必要な権限
    permission_required = "plan.add_koujiname"
    # 権限がない場合、Forbidden 403を返す。これがない場合はログイン画面に飛ばす。
    raise_exception = True

    # 保存が成功した場合に遷移するurl
    def get_success_url(self):
        return reverse_lazy("repair_plan:create_koujitype")

    def form_valid(self, form):
        """上手く保存メッセージを表示できない？"""
        messages.success(self.request, "保存しました。")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.warning(self.request, "保存できませんでした。")
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["masterlist"] = MasterKoujiType.objects.all().order_by(
            "-live", "sequense"
        )
        return context


class UpdateKoujiTypeView(PermissionRequiredMixin, generic.UpdateView):
    """修繕費支出項目マスターを修正する"""

    model = MasterKoujiType
    form_class = MasterKoujiTypeForm
    template_name = "plan/master_koujitype_form.html"
    # 必要な権限
    permission_required = "plan.add_koujiname"
    # 権限がない場合、Forbidden 403を返す。これがない場合はログイン画面に飛ばす。
    raise_exception = True

    # 保存が成功した場合に遷移するurl
    def get_success_url(self):
        return reverse_lazy("repair_plan:create_koujitype")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["masterlist"] = MasterKoujiType.objects.all().order_by("sequense")
        return context


class CreateMasterUnitView(PermissionRequiredMixin, generic.CreateView):
    """数量単位マスターを登録する。
    マスターデータは、数が多くはないので表示しながら入力formを表示させる。
    データが存在すれば表示し、修正か新規登録させる。
    listでページングする場合は https://torina.top/detail/337/#i3 を参照。
    """

    model = MasterUnit
    form_class = MasterUnitForm
    template_name = "plan/master_unit_form.html"
    # 必要な権限
    permission_required = "plan.add_koujiname"
    # 権限がない場合、Forbidden 403を返す。これがない場合はログイン画面に飛ばす。
    raise_exception = True

    # 保存が成功した場合に遷移するurl
    def get_success_url(self):
        return reverse_lazy("repair_plan:create_masterunit")

    def form_valid(self, form):
        """上手く保存メッセージを表示できない？"""
        messages.success(self.request, "保存しました。")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.warning(self.request, "保存できませんでした。")
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["masterlist"] = MasterUnit.objects.all()
        return context
