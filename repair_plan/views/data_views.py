import logging

from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models.aggregates import Max
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import generic

from repair_plan.forms import (
    DeleteKoujinameVerForm,
    DuplicateRepairPlanForm,
    MasterPlanCreateForm,
    RepairPlanCreateForm,
    RepairPlanUpdateForm,
)
from repair_plan.models import KoujiName, MasterPlan
from repair_plan.views.list_views import RepairPlanListView

logger = logging.getLogger(__name__)


class CreateRepairPlanView(PermissionRequiredMixin, generic.CreateView):
    """長期修繕計画データを登録する
    http://k-mawa.hateblo.jp/entry/2017/10/20/181711
    """

    model = KoujiName
    form_class = RepairPlanCreateForm
    template_name = "plan/repair_plan_form.html"
    # 必要な権限(admin以外で下記の権限を持つユーザーが利用可能)
    permission_required = "plan.add_koujiname"
    # 権限がない場合、Forbidden 403を返す。これがない場合はログイン画面に飛ばす。
    raise_exception = True
    # 保存が成功した場合に遷移するurl。再度入力画面に遷移する。
    success_url = reverse_lazy("repair_plan:add_repair_plan")

    def form_valid(self, form):
        messages.success(self.request, "保存しました。")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.warning(self.request, "保存できませんでした。")
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        title = "長期修繕計画データの登録"
        context["title"] = title
        # formに初期値を表示させる。
        ver = MasterPlan.objects.aggregate(ver=Max("version"))["ver"]
        context["form"] = RepairPlanCreateForm(
            initial={"version": ver, "kouji_quantity": 1, "unit": 1}
        )
        return context


class UpdateRepairPlanListView(RepairPlanListView):
    """長期修繕計画の編集用list表示
    - ToDo
    - templateファイルで管理者の場合、「編集・削除」ボタンを表示するようにすれば、
      わざわざ編集用のVieteファイルを表示するだけのviewクラスを作成する必要はない。どちらがスマートか？
    """

    def get_template_names(self):
        """templateファイルをuser agentで切り替える"""
        if self.request.user_agent_flag == "mobile":
            template_name = "plan/update_repair_plan_list.html"
        else:
            template_name = "plan/update_repair_plan_list.html"
        return [template_name]


class UpdateRepairPlanView(PermissionRequiredMixin, generic.UpdateView):
    """長期修繕計画UPDATE"""

    model = KoujiName
    form_class = RepairPlanUpdateForm
    template_name = "plan/repair_plan_form.html"
    # 必要な権限（データ登録できる権限は共通）
    permission_required = "plan.add_koujiname"
    # 権限がない場合、Forbidden 403を返す。これがない場合はログイン画面に飛ばす。
    raise_exception = True

    # 保存が成功した場合に遷移するurl
    def get_success_url(self):
        qs = KoujiName.objects.filter(pk=self.object.pk).values(
            "version__version", "kouji_type"
        )
        ver = qs[0]["version__version"]
        koujitype = qs[0]["kouji_type"]
        return reverse_lazy(
            "repair_plan:update_repair_plan_list",
            kwargs={"version": ver, "kouji_type": koujitype},
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        title = "長期修繕計画データの修正"
        context["title"] = title
        return context


class DeleteRepairPlanView(PermissionRequiredMixin, generic.DeleteView):
    """個別工事項目の削除View"""

    model = KoujiName
    # 削除してよいか確認するためのtemplate
    template_name = "plan/delete_confirm.html"
    # 必要な権限（データ登録できる権限は共通）
    permission_required = "plan.add_koujiname"
    # 権限がない場合、Forbidden 403を返す。これがない場合はログイン画面に飛ばす。
    raise_exception = True
    # 削除が成功した場合に遷移するurl
    success_url = reverse_lazy("repair_plan:update_repair_plan_list")


class DuplicateRepairPlanView(PermissionRequiredMixin, generic.FormView):
    form_class = DuplicateRepairPlanForm
    template_name = "plan/duplicate_plan_form.html"
    success_url = reverse_lazy("repair_plan:repair_plan_list")
    permission_required = "plan.add_koujiname"

    def get_context_data(self, **kwargs):
        """コンテキストデータにタイトルとマスタプランリストを追加
        - formは自動で追加される。
        - formだけならgetメソッドをオーバーライドしても良いが、今回はcontext_dataにまとめて追加する。
            def get(self, request, *args, **kwargs):
                form = self.form_class()
                return render(request, self.template_name, {"form": form})
        """
        context = super().get_context_data(**kwargs)
        context["title"] = "長期修繕計画の複製作成"
        context["masterlist"] = MasterPlan.objects.all().order_by("-version")
        return context

    def post(self, request, *args, **kwargs):
        """フォームのPOSTデータを処理して長期修繕計画を複製する"""
        # フォームのバリデーション
        form = self.form_class(request.POST)
        if not form.is_valid():
            return render(request, self.template_name, {"form": form})

        # フォームから値を取得
        source_master = form.cleaned_data["source_ver"]  # MasterPlan インスタンス
        new_ver = form.cleaned_data["new_ver"]  # 整数

        # 既存チェック
        if MasterPlan.objects.filter(version=new_ver).exists():
            messages.info(request, f"バージョン {new_ver} のデータは既に存在します。")
            return redirect(self.get_success_url())

        # 新 MasterPlan 作成
        new_master = MasterPlan.objects.create(
            version=new_ver,
            first_year=source_master.first_year,
            final_year=source_master.final_year,
            balance=source_master.balance,
            comment=source_master.comment,
        )

        # KoujiName の複製
        old_kouji = KoujiName.objects.filter(version=source_master)
        new_plan = []

        for d in old_kouji:
            new_plan.append(
                KoujiName(
                    version=new_master,
                    do_calc=d.do_calc,
                    kouji_type=d.kouji_type,
                    kouji_name=d.kouji_name,
                    kouji_spec=d.kouji_spec,
                    kouji_quantity=d.kouji_quantity,
                    unit=d.unit,
                    unit_price=d.unit_price,
                    kouji_year=d.kouji_year,
                    comment=d.comment,
                    actual_cost=d.actual_cost,
                    complete=d.complete,
                )
            )

        # 一括作成
        KoujiName.objects.bulk_create(new_plan)

        msg = f"バージョン {source_master.version} → {new_ver} の複製が完了しました"
        messages.info(request, msg)

        return redirect(self.get_success_url())


class MasterPlanCreateView(PermissionRequiredMixin, generic.CreateView):
    """計画初年度の修繕費会計残高を登録/修正する"""

    model = MasterPlan
    form_class = MasterPlanCreateForm
    template_name = "plan/masterplan_form.html"
    # 必要な権限（管理者権限）
    permission_required = "plan.add_koujiname"
    # 権限がない場合、Forbidden 403を返す。これがない場合はログイン画面に飛ばす。
    raise_exception = True

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


class MasterPlanUpdateView(PermissionRequiredMixin, generic.UpdateView):
    """計画初年度の修繕費会計残高を修正する"""

    model = MasterPlan
    form_class = MasterPlanCreateForm
    template_name = "plan/masterplan_form.html"
    # 必要な権限（管理者権限）
    permission_required = "plan.add_koujiname"
    # 権限がない場合、Forbidden 403を返す。これがない場合はログイン画面に飛ばす。
    raise_exception = True

    # 保存が成功した場合に遷移するurl
    def get_success_url(self):
        return reverse_lazy("repair_plan:create_master_plan")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["masterlist"] = MasterPlan.objects.all().order_by("-version")
        return context


class DeleteKoujiNameByVerView(PermissionRequiredMixin, generic.FormView):
    """指定されたversionのKoujiNameデータを削除する"""

    template_name = "plan/delete_koujiname_ver.html"
    form_class = DeleteKoujinameVerForm
    # 必要な権限（管理者権限）
    permission_required = "plan.add_koujiname"
    success_url = reverse_lazy("repair_plan:delete_koujiname_ver")

    def form_valid(self, form):
        # フォームのデータを処理する
        # このメソッドはPOSTリクエストが有効な場合に呼び出される
        del_version = form.cleaned_data["keikaku_ver"]
        yesno = form.cleaned_data["confirm_flg"]
        if yesno:
            msg = KoujiName.objects.delete_koujiname_by_ver(del_version)
            messages.success(self.request, msg)
        else:
            messages.success(self.request, "削除確認がありません")
        return super().form_valid(form)
