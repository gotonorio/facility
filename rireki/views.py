import logging
from datetime import datetime

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import Max, Q, Sum
from django.urls import reverse_lazy
from django.views import generic

from .forms import KoujiRirekiCreateForm, RirekiListForm
from .models import KoujiRireki

logger = logging.getLogger(__name__)


class RirekiListView(LoginRequiredMixin, generic.TemplateView):
    """個別工事リスト"""

    model = KoujiRireki
    # form_classはどのような時に必要か？
    form_class = RirekiListForm
    # TemplateViewの場合はtemplate_nameは必須．
    template_name = "rireki/rireki_list.html"

    def get_template_names(self):
        """templateファイルを切り替える"""
        if self.request.user_agent_flag == "mobile":
            template_name = "rireki/rireki_list.html"
        else:
            template_name = "rireki/rireki_list.html"
        return [template_name]

    # get_context_data の引数の kwargs には、urls.py で指定した名前つきの
    # 正規表現のプレースホルダにマッチした内容が入ってくるが、
    # この内容は self.kwargs にも入っていてアクセスできる。
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_name = self.request.user
        # formのselect要素の値を得る
        kouji_type = self.request.GET.get("kouji_type", None)
        ac_type = self.request.GET.get("account_type", None)
        yyyy = KoujiRireki.objects.aggregate(year=Max("year"))["year"]
        # 初期値を設定。
        year = self.request.GET.get("year", yyyy)

        # ''が返された時の処理
        if kouji_type == "":
            kouji_type = None
        if ac_type == "":
            ac_type = None
        if year == "":
            year = None

        # Qオブジェクト作成（and結合なのでfilterでも可）
        koujitype_q = Q()
        actype_q = Q()
        year_q = Q()
        total = 0
        if kouji_type:
            koujitype_q = Q(koujitype=kouji_type)
        if ac_type:
            actype_q = Q(account_type=ac_type)
        if year:
            year_q = Q(year=year)
        sql = KoujiRireki.objects.filter(koujitype_q & actype_q & year_q).order_by("year", "month")
        # コストの合計を計算する
        total = sql.aggregate(Sum("cost"))

        # formのselectに初期値を設定する．http://i2bskn.hateblo.jp/entry/20120826/1345936779
        form = RirekiListForm(initial={"kouji_type": kouji_type, "account_type": ac_type, "year": year})

        # # コストの合計を計算する
        # total = KoujiRireki.calc_total(self, sql)
        context["total"] = total["cost__sum"]
        context["user_name"] = user_name
        context["form"] = form
        context["rirekilist"] = sql
        context["start_year"] = -settings.INITIAL_YEAR
        return context


class RirekiDetailView(LoginRequiredMixin, generic.DetailView):
    """工事履歴の詳細画面表示"""

    model = KoujiRireki
    context_object_name = "kouji_detail"

    def get_template_names(self):
        """templateファイルを切り替える"""
        if self.request.user_agent_flag == "mobile":
            template_name = "rireki/rireki_detail_pc.html"
        else:
            template_name = "rireki/rireki_detail_pc.html"
        return [template_name]

    pass


class KoujiRirekiCreateView(PermissionRequiredMixin, generic.CreateView):
    """工事実績の登録"""

    model = KoujiRireki
    form_class = KoujiRirekiCreateForm
    template_name = "rireki/kouji_rireki_form.html"
    permission_required = "repair_plan.add_koujiname"
    success_url = reverse_lazy("rireki:rireki_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "工事履歴の登録"
        return context

    def get_initial(self):
        """formに初期値を設定"""
        initial = super().get_initial()
        this_year = datetime.now().year
        initial["year"] = this_year
        return initial

    def form_valid(self, form):
        messages.success(self.request, "保存しました。")
        logger.info(f"create {self.object} by {self.request.user} ")
        return super().form_valid(form)


class RirekiUpdateListView(PermissionRequiredMixin, generic.ListView):
    model = KoujiRireki
    template_name = "rireki/update_list.html"
    permission_required = "repair_plan.add_koujiname"
    queryset = KoujiRireki.objects.all().order_by("-year")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        yyyy = KoujiRireki.objects.aggregate(year=Max("year"))["year"]
        if self.kwargs:
            # update後にget_success_url()で遷移するためにkwargsにデータがセットされている。
            ac_type = self.request.GET.get("account_type")
            year = self.kwargs.get("year")
            kouji_type = self.kwargs.get("kouji_type")
        else:
            ac_type = self.request.GET.get("account_type")
            year = self.request.GET.get("year", yyyy)
            kouji_type = self.request.GET.get("kouji_type")

        # Qオブジェクト作成
        koujitype_q = Q()
        actype_q = Q()
        year_q = Q()
        if kouji_type:
            koujitype_q = Q(koujitype=kouji_type)
        if ac_type:
            actype_q = Q(account_type=ac_type)
        if year:
            year_q = Q(year=year)
        sql = KoujiRireki.objects.filter(koujitype_q & actype_q & year_q).order_by("-year")

        # formのselectに初期値を設定する．http://i2bskn.hateblo.jp/entry/20120826/1345936779
        form = RirekiListForm(initial={"kouji_type": kouji_type, "account_type": ac_type, "year": year})

        context["start_year"] = -settings.INITIAL_YEAR
        context["form"] = form
        context["update_list"] = sql
        return context


class RirekiUpdateView(PermissionRequiredMixin, generic.UpdateView):
    """Update処理後にkwargsを使って元の画面に戻る"""

    model = KoujiRireki
    form_class = KoujiRirekiCreateForm
    template_name = "rireki/kouji_rireki_form.html"
    # 必要な権限（データ登録できる権限は共通）
    permission_required = "repair_plan.add_koujiname"
    # 権限がない場合、Forbidden 403を返す。これがない場合はログイン画面に飛ばす。
    raise_exception = True
    # 必要なクラス変数を宣言しておく。
    ac_type = 0
    year = 0
    kouji_type = 0

    def get_success_url(self):
        return reverse_lazy(
            "rireki:update_list",
            kwargs={"account_type": self.ac_type, "year": self.year, "kouji_type": self.kouji_type},
        )

    def form_valid(self, form):
        messages.success(self.request, "アップデートしました。")
        # formデータからリダイレクト用のkwargs引数を取得する。
        self.ac_type = form.cleaned_data["account_type"].pk
        self.year = form.cleaned_data["year"]
        self.kouji_type = form.cleaned_data["koujitype"].pk
        return super().form_valid(form)


class RirekiDeleteView(PermissionRequiredMixin, generic.DeleteView):
    """"""

    model = KoujiRireki
    template_name = "rireki/confirm_delete.html"
    permission_required = "repair_plan.add_koujiname"
    success_url = reverse_lazy("rireki:rireki_list")  # 削除成功後のリダイレクト先
