from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordChangeForm,
    UserCreationForm,
)
from django.contrib.auth.models import Group

User = get_user_model()


class LoginForm(AuthenticationForm):
    """ログインフォーム"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "input is-size-6"
            field.widget.attrs["placeholder"] = field.label


class TempUserCreateForm(UserCreationForm):
    """ユーザー仮登録用フォーム
    emailを必須フィールドにするため上書きする。
    """

    username = forms.CharField(label="ユーザ名")
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = (
            "username",
            "email",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "input"


class UserUpdateForm(forms.ModelForm):
    """管理者が仮ユーザーのis_activeフラグを更新するフォーム"""

    username = forms.CharField(label="ユーザ名", required=True)
    is_active = forms.NullBooleanField(label="有効")

    group = forms.ModelChoiceField(
        empty_label="Group選択",
        queryset=Group.objects.all(),
        required=True,
        widget=forms.Select(attrs={"class": "select-css"}),
    )

    class Meta:
        model = User
        fields = ("username", "email", "is_active")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs["class"] = "input"
        self.fields["email"].widget.attrs["class"] = "input"
        self.fields["is_active"].widget.attrs["class"] = "select-css"


class PasswordUpdateForm(PasswordChangeForm):
    """ユーザーが自分のパスワードを更新するためのフォーム"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "input"
