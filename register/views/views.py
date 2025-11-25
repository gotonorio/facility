# from control.models import ControlRecord
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.views import generic
from register.forms import LoginForm

User = get_user_model()


class Login(LoginView):
    """ログインページ"""

    form_class = LoginForm
    template_name = "register/login.html"

    # def get_context_data(self, **kwargs):
    #     """ログインページで仮登録メニューを表示させる"""
    #     context = super().get_context_data(**kwargs)
    #     qs = ControlRecord.objects.values("tmp_user_flg")
    #     if qs.exists():
    #         context["tmp_user_flg"] = qs[0]["tmp_user_flg"]
    #     return context


class Logout(LoginRequiredMixin, LogoutView):
    """ログアウトページ"""

    template_name = "register/logout.html"


class MypageView(LoginRequiredMixin, generic.TemplateView):
    """モバイル対応"""

    def get_template_names(self):
        """templateファイルを切り替える"""
        if self.request.user_agent_flag == "mobile":
            template_name = "register/mypage.html"
            # template_name = "register/mypage_mobile.html"
        else:
            template_name = "register/mypage.html"
        return [template_name]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user"] = self.request.user
        context["user_id"] = self.request.user.id
        return context


class FacilityView(LoginRequiredMixin, generic.TemplateView):
    """設備台帳のメインページ"""

    def get_template_names(self):
        """templateファイルを切り替える"""
        if self.request.user_agent_flag == "mobile":
            template_name = "register/facility/facility.html"
            # template_name = "register/facility/facility_mobile.html"
        else:
            template_name = "register/facility/facility.html"
        return [template_name]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user"] = self.request.user
        context["user_id"] = self.request.user.id
        return context


class RepairPlanView(LoginRequiredMixin, generic.TemplateView):
    """長期修繕計画のメインページ"""

    def get_template_names(self):
        """templateファイルを切り替える"""
        if self.request.user_agent_flag == "mobile":
            template_name = "register/repair_plan/repair_plan.html"
            # template_name = "register/repair_plan/repairplan_mobile.html"
        else:
            template_name = "register/repair_plan/repair_plan.html"
        return [template_name]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user"] = self.request.user
        context["user_id"] = self.request.user.id
        return context


class RepairPlanDataView(LoginRequiredMixin, generic.TemplateView):
    """長期修繕計画のデータ管理ページ"""

    template_name = "register/repair_plan/repair_plan_data.html"
