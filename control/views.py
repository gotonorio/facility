import datetime
import os
import shutil

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import generic

from control.forms import DescriptionCreateForm, DescriptionListForm, UpdateControlForm
from control.models import ControlRecord, Description


class ControlRecordListView(PermissionRequiredMixin, generic.ListView):
    model = ControlRecord
    template_name = "control/control_list.html"
    permission_required = "register.add_user"


class ControlRecordUpdateView(PermissionRequiredMixin, generic.UpdateView):
    """コントロールデータのアップデート"""

    model = ControlRecord
    form_class = UpdateControlForm
    template_name = "control/control_form.html"
    permission_required = "register.add_user"
    # 保存が成功した場合に遷移するurl
    success_url = reverse_lazy("register:mypage")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "コントロールデータの修正"
        return context


def backupDB(request):
    """DBのバックアップ処理
    静的ページに戻さざるを得ない？
    """
    # DBコピー
    now = datetime.datetime.now()
    db_file_name = f"{now.year}-{now.month}-{now.day}-{now.hour}-{now.minute}-({request.user}).sqlite3"
    backup_path = f"./backupDB/{db_file_name}"
    shutil.copy("./fac.sqlite3", backup_path)
    # backupファイルのリスト
    file_list = os.listdir("./backupDB")
    # もし10を超えたら古いバックアップを削除する。
    if len(file_list) >= settings.BACKUP_NUM:
        file_list.sort()
        # ソートした結果の最初（古い）ファイルを削除する。
        os.remove("./backupDB/" + file_list[0])

    # master_pageに戻る。
    # https://docs.djangoproject.com/en/4.0/ref/contrib/messages/
    # https://stackoverflow.com/questions/51155947/django-redirect-to-another-view-with-context
    messages.info(request, f"DBをバックアップしました。 ファイル名:{db_file_name}")
    return redirect("register:mypage")


class DescriptionView(LoginRequiredMixin, generic.TemplateView):
    """プログラムの説明文表示"""

    model = Description

    def get_template_names(self):
        """templateファイルを切り替える"""
        if self.request.user_agent_flag == "mobile":
            template_name = "control/description.html"
        else:
            template_name = "control/description.html"
        return [template_name]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pk = self.request.GET.get("title", False)
        if pk == "" or pk is False:
            qs = None
        else:
            qs = Description.objects.get(pk=pk)

        form = DescriptionListForm(
            initial={
                "title": pk,
            }
        )
        context["qs"] = qs
        context["form"] = form
        return context


class DescriptionCreateView(PermissionRequiredMixin, generic.CreateView):
    """説明文モデルを作成"""

    model = Description
    form_class = DescriptionCreateForm
    permission_required = "repair_plan.add_koujiname"
    template_name = "control/description_form.html"
    success_url = reverse_lazy("register:repair_plan")


class DescriptionUpdateView(PermissionRequiredMixin, generic.UpdateView):
    """説明文モデルのアップデート"""

    model = Description
    form_class = DescriptionCreateForm
    permission_required = "repair_plan.add_koujiname"
    template_name = "control/description_form.html"
    success_url = reverse_lazy("control:description")


class DescriptionDeleteView(PermissionRequiredMixin, generic.DeleteView):
    model = Description
    template_name = "control/description_delete_confirm.html"
    permission_required = "repair_plan.add_koujiname"
    success_url = reverse_lazy("control:description")

    # def get_success_url(self):
    #     """ 削除した後 """
    #     qs = Description.objects.filter(pk=self.object.pk).values('title', 'created_date')
    #     title = qs[0]['title']
    #     return reverse_lazy('control:description', kwargs={'title': title, })
