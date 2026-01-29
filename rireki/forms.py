from django import forms

from repair_plan.models import MasterKoujiType

from .models import AccountType, KoujiRireki


class RirekiListForm(forms.Form):
    """履歴一覧表示用Form
    http://www.subthread.co.jp/blog/20160531/
    別テーブルのレコードを選択させ、その ID を元に検索したい場合は、forms.ModelChoiceField() を使う。
    単に選択肢を表示させたい場合は、forms.ChoiceField() を使う。
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
        # bulmaの select クラスを適用する場合は、DjangoではなくHTMLテンプレート側で指定すること
        # widget=forms.Select(attrs={"class": "select"}),
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
        # bulmaの select クラスを適用する場合は、DjangoではなくHTMLテンプレート側で指定すること
        # widget=forms.Select(attrs={"class": "selects"}),
    )

    year = forms.ChoiceField(
        label="西暦",
        required=False,  # 全表示を許容するためFalseに
    )

    def __init__(self, *args, **kwargs):
        """ChoiceFieldの選択肢をDBから動的に取得してセットする場合は、__init__をオーバーライドする"""
        super().__init__(*args, **kwargs)

        # 1. DBから年度リストを取得
        year_values = (
            KoujiRireki.objects.values_list("year", flat=True)
            .order_by("-year")
            .distinct()
        )
        # 2. 先頭に「年度全表示」を追加してセットする
        # (値, ラベル) の形式
        self.fields["year"].choices = [("", "年度全表示")] + [
            (v, v) for v in year_values
        ]


class ImportForm(forms.Form):
    file = forms.FileField(
        label="CSVファイル",
        help_text="※拡張子csvのファイルをアップロードしてください。",
    )

    # BulmaがFileFieldの選択ボタンに未対応？
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["file"].widget.attrs["class"] = "is-size-6"


class KoujiRirekiCreateForm(forms.ModelForm):
    """工事履歴登録用フォーム"""

    class Meta:
        model = KoujiRireki
        fields = [
            "year",
            "month",
            "koujitype",
            "koujimei",
            "cost",
            "constractor",
            "account_type",
            "comment",
        ]
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
