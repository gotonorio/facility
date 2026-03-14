# from datetime import date

from django import forms

from common.forms.base_form import YearMonthForm

KIND = (
    ("parking", "駐車場"),
    ("bicycle", "自転車置場"),
    ("motorcycle", "バイク置場"),
)


class KuraselTranslatorForm(YearMonthForm):
    """クラセルデータ取り込み用ベースForm"""

    note = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "placeholder": "ヘッダー部を除いてコピーしてください。",
                "class": "textarea",
                "rows": 10,
            }
        ),
        label="内容",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["year"].widget.attrs["class"] = "input"
        self.fields["month"].widget.attrs["class"] = "select-css"
