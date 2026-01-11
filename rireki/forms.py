from django import forms
from repair_plan.models import MasterKoujiType

from .models import AccountType, KoujiRireki


class RirekiListForm(forms.Form):
    """履歴一覧表示の時にselect要素で工事種別を選択させる
    http://www.subthread.co.jp/blog/20160531/
    """

    # querysetを使う場合はforms.ModelChoiceFiled()を使う。empty_labelを使用できる。
    account_type = forms.ModelChoiceField(
        queryset=AccountType.objects.all(),
        label="会計区分",
        empty_label="会計区分全表示",
        error_messages={
            "required": "You didn't select a choice.",
            "invalid_choice": "invalid choice.",
        },
        required=False,
        widget=forms.Select(attrs={"class": "select-css"}),
    )
    kouji_type = forms.ModelChoiceField(
        queryset=MasterKoujiType.objects.filter(live="1").order_by("sequense"),
        label="工事種別",
        empty_label="工事種別全表示",
        error_messages={
            "required": "You didn't select a choice.",
            "invalid_choice": "invalid choice.",
        },
        required=False,
        widget=forms.Select(attrs={"class": "select-css"}),
    )
    year = forms.ModelChoiceField(
        # 修繕履歴データから西暦を抽出してセットする。
        queryset=KoujiRireki.objects.values_list("year", flat=True).order_by("year").distinct(),
        label="西暦",
        empty_label="年度全表示",
        error_messages={
            "required": "You didn't select a choice.",
            "invalid_choice": "invalid choice.",
        },
        required=False,
        widget=forms.Select(attrs={"class": "select-css"}),
    )

    # BulmaがFileFieldの選択ボタンに未対応？
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["account_type"].widget.attrs["class"] = "select-css is-size-7"
        self.fields["kouji_type"].widget.attrs["class"] = "select-css is-size-7"
        self.fields["year"].widget.attrs["class"] = "select-css is-size-7"


class ImportForm(forms.Form):
    file = forms.FileField(label="CSVファイル", help_text="※拡張子csvのファイルをアップロードしてください。")

    # BulmaがFileFieldの選択ボタンに未対応？
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["file"].widget.attrs["class"] = "is-size-6"


class KoujiRirekiCreateForm(forms.ModelForm):
    """工事履歴登録用フォーム"""

    class Meta:
        model = KoujiRireki
        fields = ["year", "month", "koujitype", "koujimei", "cost", "constractor", "account_type", "comment"]
        labels = {
            "year": "年",
            "month": "月",
            "koujitype": "工事種別",
            "koujimei": "工事名",
            "cost": "工事費",
            "constractor": "施工業者",
            "account_type": "会計区分",
            "comment": "備考",
        }
        widgets = {
            "year": forms.NumberInput(
                attrs={
                    "class": "input",
                }
            ),
            "month": forms.NumberInput(
                attrs={
                    "class": "input",
                }
            ),
            "koujitype": forms.Select(
                attrs={
                    "class": "select-css",
                }
            ),
            "koujimei": forms.TextInput(
                attrs={
                    "class": "input",
                }
            ),
            "cost": forms.NumberInput(
                attrs={
                    "class": "input",
                }
            ),
            "constractor": forms.TextInput(
                attrs={
                    "class": "input",
                }
            ),
            "account_type": forms.Select(
                attrs={
                    "class": "select-css",
                }
            ),
            "comment": forms.Textarea(
                attrs={
                    "class": "textarea",
                    "rows": "2",
                    "required": False,
                }
            ),
        }
