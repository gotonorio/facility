import logging

from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.utils.http import urlencode
from django.views.generic import CreateView, DeleteView, FormView, UpdateView
from repair_plan.forms import (
    DeleteKoujinameVerForm,
    DuplicateRepairPlanForm,
    MasterPlanCreateForm,
    RepairPlanCreateForm,
    RepairPlanUpdateForm,
)
from repair_plan.models import KoujiName, MasterKoujiType, MasterPlan
from repair_plan.services.data_service import (
    duplicate_repair_plan,
    get_max_master_version,
)

logger = logging.getLogger(__name__)


# --- 共通設定の継承用クラス ---
class RepairPlanAdminMixin(PermissionRequiredMixin):
    # 必要な権限（管理者権限）
    permission_required = "repair_plan.add_koujiname"
    # 権限がない場合、Forbidden 403を返す。これがない場合はログイン画面に飛ばす。
    raise_exception = True


# --- 工事データ操作 ---
class ReparPlanCreateView(RepairPlanAdminMixin, CreateView):
    """工事データの登録"""

    model = KoujiName
    form_class = RepairPlanCreateForm
    template_name = "repair_plan/repair_plan_form.html"
    success_url = reverse_lazy("repair_plan:add_repair_plan")

    def get_initial(self):
        return {"version": get_max_master_version(), "kouji_quantity": 1, "unit": 1}

    def form_valid(self, form):
        messages.success(self.request, "保存しました。")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        title = "長期修繕計画データの作成"
        context["title"] = title
        return context


class RepairPlanUpdateView(RepairPlanAdminMixin, UpdateView):
    """工事データの修正"""

    model = KoujiName
    form_class = RepairPlanUpdateForm
    template_name = "repair_plan/repair_plan_form.html"

    def get_success_url(self):
        # 修正後、元のリスト画面（同じVer/種別）に戻す
        base_url = reverse("repair_plan:repairplan_update_list")
        # クエリパラメータを辞書形式で定義
        kouji_type_id = MasterKoujiType.get_koujitype_id(self.object.kouji_type)

        params = urlencode(
            {
                "version": self.object.version.version,
                "koujitype": kouji_type_id,
            }
        )
        return f"{base_url}?{params}"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        title = "長期修繕計画データの修正"
        context["title"] = title
        return context


class RepairPlanDuplicateView(RepairPlanAdminMixin, FormView):
    """修繕計画の複製作成（最重要ロジック）"""

    form_class = DuplicateRepairPlanForm
    template_name = "repair_plan/duplicate_plan_form.html"
    success_url = reverse_lazy("repair_plan:repairplan_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["masterlist"] = MasterPlan.objects.all().order_by("-version")
        return context

    def form_valid(self, form):
        source_ver = form.cleaned_data["source_ver"]
        new_ver = form.cleaned_data["new_ver"]

        # Service呼び出し
        success = duplicate_repair_plan(
            source_plan=source_ver,
            new_version=new_ver,
            author=self.request.user,
        )
        if success:
            message = f"Ver.{source_ver} を Ver.{new_ver} として複製しました。"
        else:
            message = "複製に失敗しました"
        messages.info(self.request, message)
        return redirect(self.get_success_url())


# --- バージョン（一括）操作 ---
class KoujiNameDeleteView(RepairPlanAdminMixin, FormView):
    """バージョン単位の修繕計画データを一括削除"""

    template_name = "repair_plan/delete_koujiname_ver.html"
    form_class = DeleteKoujinameVerForm
    success_url = reverse_lazy("repair_plan:delete_koujiname_ver")

    def form_valid(self, form):
        if not form.cleaned_data["confirm_flg"]:
            messages.warning(self.request, "削除確認チェックを入れてください。")
            return self.form_invalid(form)

        # form.cleaned_data["version"]はバージョン番号
        _ = KoujiName.objects.delete_koujiname_by_ver(form.cleaned_data["version"])
        messages.success(self.request, f"バージョン {form.cleaned_data['version']} を削除しました。")
        return super().form_valid(form)


class MasterPlanCreateView(RepairPlanAdminMixin, CreateView):
    """修繕計画マスタプランの登録/修正"""

    model = MasterPlan
    form_class = MasterPlanCreateForm
    template_name = "repair_plan/masterplan_form.html"

    # 保存が成功した場合に遷移するurl
    def get_success_url(self):
        return reverse_lazy("repair_plan:create_master_plan")

    def form_valid(self, form):
        return super().form_valid(form)

    def form_invalid(self, form):
        """上手く保存メッセージを表示できない？"""
        messages.warning(self.request, "保存できませんでした。")
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["masterlist"] = MasterPlan.objects.all().order_by("-version")
        return context


class MasterPlanUpdateView(RepairPlanAdminMixin, UpdateView):
    """計画初年度の修繕費会計残高を修正する"""

    model = MasterPlan
    form_class = MasterPlanCreateForm
    template_name = "repair_plan/masterplan_form.html"

    # 保存が成功した場合に遷移するurl
    def get_success_url(self):
        return reverse_lazy("repair_plan:create_master_plan")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["masterlist"] = MasterPlan.objects.all().order_by("-version")
        return context


class RepairPlanDeleteView(RepairPlanAdminMixin, DeleteView):
    """個別工事項目の削除View"""

    model = KoujiName
    # 削除してよいか確認するためのtemplate
    template_name = "repair_plan/delete_confirm.html"
    # 削除が成功した場合に遷移するurl
    # success_url = reverse_lazy("repair_plan:repairplan_update_list")

    def get_success_url(self):
        # 修正後、元のリスト画面（同じVer/種別）に戻す
        base_url = reverse("repair_plan:repairplan_update_list")
        # クエリパラメータを辞書形式で定義
        kouji_type_id = MasterKoujiType.get_koujitype_id(self.object.kouji_type)
        params = urlencode(
            {
                "version": self.object.version.version,
                "koujitype": kouji_type_id,
            }
        )
        return f"{base_url}?{params}"

    def form_valid(self, request, *args, **kwargs):
        # 削除実行時にメッセージを表示させる（オプション）
        result = super().delete(request, *args, **kwargs)
        messages.success(self.request, "データを削除しました。")
        return result
