from django import forms

from control.models import ControlRecord, Description


class UpdateControlForm(forms.ModelForm):
    """仮登録メニューの表示/非表示を設定"""

    class Meta:
        model = ControlRecord
        fields = ("tmp_user_flg",)
        labels = {
            "tmp_user_flg": "仮登録表示",
        }
        widgets = {
            "tmp_user_flg": forms.NullBooleanSelect(
                attrs={
                    "class": "select-css",
                }
            ),
        }


class DescriptionCreateForm(forms.ModelForm):
    """データ入力説明文作成用フォーム"""

    class Meta:
        """https://docs.djangoproject.com/en/4.0/topics/forms/modelforms/#overriding-the-default-fields"""

        model = Description
        fields = ["title", "description", "alive", "only_manager"]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "input",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "textarea",
                    "placeholder": "概要説明",
                    "rows": "16",
                }
            ),
        }


class DescriptionListForm(forms.ModelForm):
    """説明書表示用Form"""

    class Meta:
        model = Description
        fields = [
            "title",
        ]

    title = forms.ModelChoiceField(
        queryset=Description.objects.filter(alive=True),
        label="タイトル",
        empty_label="目次",
        error_messages={
            "required": "You didn't select a choice.",
            "invalid_choice": "invalid choice.",
        },
        required=False,
        initial="ALL",
        widget=forms.Select(attrs={"class": "select-css is-size-7"}),
    )
