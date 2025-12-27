import datetime
import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import generic

from .forms import (
    ShoukakiDisposalForm,
    ShoukakiForm,
    ShoukakiListForm,
    ShoukakiTypeForm,
)
from .models import Shoukaki, ShoukakiType

logger = logging.getLogger(__name__)


class ShoukakiListView(LoginRequiredMixin, generic.TemplateView):
    """消火器の一覧表示"""

    model = Shoukaki
    template_name = "shoukaki/shoukaki_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order = "code"
        order_no = self.request.GET.get("order")
        if order_no == "製造年":
            order = "made_year"
        elif order_no == "設置日":
            order = "installation_date"
        elif order_no == "点検日":
            order = "inspection_date"
        elif order_no == "形式":
            order = "shoukaki__keisiki"

        queryset = Shoukaki.objects.select_related("shoukaki").filter(alive=True).order_by(order)

        form = ShoukakiListForm(
            initial={
                "order": order_no,
            }
        )
        context["shoukaki_list"] = queryset
        context["form"] = form
        return context


class ShoukakiCreateView(PermissionRequiredMixin, generic.CreateView):
    """消火器データ入力"""

    model = Shoukaki
    form_class = ShoukakiForm
    template_name = "shoukaki/shoukaki_form.html"
    # 必要な権限
    permission_required = "parking.add_parkingspace"
    # 権限がない場合、Forbidden 403を返す。これがない場合はログイン画面に飛ばす。
    raise_exception = True
    # 保存が成功した場合に遷移するurl
    success_url = reverse_lazy("shoukaki:create")

    def get(self, request, *args, **kwargs):
        """フォーム画面を表示する時に動的に初期値（日付）を表示する"""
        td = timezone.localtime(timezone.now())
        year = td.year
        form = self.form_class(initial={"installation_date": td, "made_year": year})
        return render(
            request,
            self.template_name,
            {
                "form": form,
            },
        )

    def form_valid(self, form):
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)


class ShoukakiUpdateView(PermissionRequiredMixin, generic.UpdateView):
    """消火器データ修正
    部品はCreateViewと同じものを使う
    """

    model = Shoukaki
    form_class = ShoukakiForm
    template_name = "shoukaki/shoukaki_form.html"
    # 必要な権限
    permission_required = "parking.add_parkingspace"
    # 権限がない場合、Forbidden 403を返す。これがない場合はログイン画面に飛ばす。
    raise_exception = True
    # 保存が成功した場合に遷移するurl
    success_url = reverse_lazy("shoukaki:update_list")

    def form_valid(self, form):
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.warning(self.request, "保存できませんでした。")
        return super().form_invalid(form)


class ShoukakiUpdateListView(LoginRequiredMixin, generic.ListView):
    """修正するための消火器の一覧表示"""

    model = Shoukaki
    template_name = "shoukaki/shoukaki_update_list.html"
    paginate_by = 90

    def get_queryset(self, **kwargs):
        queryset = super().get_queryset(**kwargs)
        queryset = queryset.select_related("shoukaki").order_by("code")
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["update"] = True
        return context


class ShoukakiTypeListView(LoginRequiredMixin, generic.ListView):
    """消火器種別データ修正のための一覧表示"""

    model = ShoukakiType
    template_name = "shoukaki/shoukakitype_list.html"

    def get_queryset(self, **kwargs):
        """order_by句を追加するために上書きする"""
        queryset = super().get_queryset(**kwargs)
        queryset = queryset.order_by("shoukaki_type")
        return queryset


class ShoukakiTypeCreateView(PermissionRequiredMixin, generic.CreateView):
    """消火器種別データ入力"""

    model = ShoukakiType
    form_class = ShoukakiTypeForm
    template_name = "shoukaki/shoukakitype_form.html"
    # 必要な権限
    permission_required = "parking.add_parkingspace"
    # 権限がない場合、Forbidden 403を返す。これがない場合はログイン画面に飛ばす。
    raise_exception = True
    # 保存が成功した場合に遷移するurl
    success_url = reverse_lazy("shoukaki:typelist")


class ShoukakiTypeUpdateView(PermissionRequiredMixin, generic.UpdateView):
    """消火器種別データ修正
    部品はCreateViewと同じものを使う
    """

    model = ShoukakiType
    form_class = ShoukakiTypeForm
    template_name = "shoukaki/shoukakitype_form.html"
    # 必要な権限
    permission_required = "parking.add_parkingspace"
    # 権限がない場合、Forbidden 403を返す。これがない場合はログイン画面に飛ばす。
    raise_exception = True
    # 保存が成功した場合に遷移するurl
    success_url = reverse_lazy("shoukaki:typelist")

    def form_invalid(self, form):
        messages.warning(self.request, "保存できませんでした。")
        return super().form_invalid(form)


class ShoukakiDisposalView(LoginRequiredMixin, generic.TemplateView):
    """廃棄する消火器一覧
    - 蓄圧式消火器は製造年の翌年から6年目に交換する
    """

    model = Shoukaki

    def get_template_names(self):
        """templateファイルを切り替える"""
        if self.request.user_agent_flag == "mobile":
            template_name = "shoukaki/discard_shoukaki.html"
            # template_name = "shoukaki/mobile/inspect_mobile.html"
        else:
            template_name = "shoukaki/discard_shoukaki.html"
        return [template_name]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        this_year = datetime.date.today().year
        year = self.request.GET.get("year", this_year)
        check = int(year) - settings.DISPOSAL_SHOUKAKI

        # 5年を超える消火器
        qs = (
            Shoukaki.objects.select_related("shoukaki")
            .filter(alive=True)
            .filter(made_year__lte=check)
            .order_by("made_year")
        )
        # form既定値
        form = ShoukakiDisposalForm(
            initial={
                "year": year,
            }
        )
        context["shoukaki_list"] = qs
        context["form"] = form
        context["index"] = "disposal"

        return context
