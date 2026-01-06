import datetime

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from django.views import generic

from .forms import ShoukakiDisposalForm, ShoukakiForm, ShoukakiListForm, ShoukakiTypeForm
from .models import Shoukaki, ShoukakiType
from .services import get_disposable_shoukaki_list, get_shoukaki_form_initial, get_sorted_shoukaki_list


class ShoukakiListView(LoginRequiredMixin, generic.TemplateView):
    """消火器の一覧表示（並べ替え機能付き）"""

    template_name = "shoukaki/shoukaki_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order_label = self.request.GET.get("order")

        # Serviceでリスト取得
        context["shoukaki_list"] = get_sorted_shoukaki_list(order_label)
        context["form"] = ShoukakiListForm(initial={"order": order_label})
        return context


class ShoukakiCreateView(PermissionRequiredMixin, generic.CreateView):
    """消火器データ入力"""

    model = Shoukaki
    form_class = ShoukakiForm
    template_name = "shoukaki/shoukaki_form.html"
    permission_required = "parking.add_parkingspace"
    raise_exception = True
    success_url = reverse_lazy("shoukaki:create")

    def get_initial(self):
        """Serviceから初期値を取得"""
        return get_shoukaki_form_initial()


class ShoukakiUpdateView(PermissionRequiredMixin, generic.UpdateView):
    """消火器データ修正"""

    model = Shoukaki
    form_class = ShoukakiForm
    template_name = "shoukaki/shoukaki_form.html"
    permission_required = "parking.add_parkingspace"
    raise_exception = True
    success_url = reverse_lazy("shoukaki:update_list")

    def form_invalid(self, form):
        messages.warning(self.request, "保存できませんでした。")
        return super().form_invalid(form)


class ShoukakiUpdateListView(LoginRequiredMixin, generic.ListView):
    """修正用の一覧表示"""

    model = Shoukaki
    template_name = "shoukaki/shoukaki_update_list.html"
    paginate_by = 90

    def get_queryset(self):
        return super().get_queryset().select_related("shoukaki").order_by("code")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["update"] = True
        return context


# --- 消火器種別 (ShoukakiType) 関連 ---


class ShoukakiTypeListView(LoginRequiredMixin, generic.ListView):
    model = ShoukakiType
    template_name = "shoukaki/shoukakitype_list.html"

    def get_queryset(self):
        return super().get_queryset().order_by("shoukaki_type")


class ShoukakiTypeCreateView(PermissionRequiredMixin, generic.CreateView):
    model = ShoukakiType
    form_class = ShoukakiTypeForm
    template_name = "shoukaki/shoukakitype_form.html"
    permission_required = "parking.add_parkingspace"
    raise_exception = True
    success_url = reverse_lazy("shoukaki:typelist")


class ShoukakiTypeUpdateView(PermissionRequiredMixin, generic.UpdateView):
    model = ShoukakiType
    form_class = ShoukakiTypeForm
    template_name = "shoukaki/shoukakitype_form.html"
    permission_required = "parking.add_parkingspace"
    raise_exception = True
    success_url = reverse_lazy("shoukaki:typelist")


# --- 廃棄・交換管理 ---


class ShoukakiDisposalView(LoginRequiredMixin, generic.TemplateView):
    """廃棄対象の消火器一覧"""

    template_name = "shoukaki/discard_shoukaki.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 基準年の取得
        this_year = datetime.date.today().year
        year = self.request.GET.get("year", this_year)

        # Serviceで廃棄リスト取得
        context["shoukaki_list"] = get_disposable_shoukaki_list(year)
        context["form"] = ShoukakiDisposalForm(initial={"year": year})
        context["index"] = "disposal"
        return context
