from django import forms
from facility.forms import YearMonthForm

from parking.models import ParkingSpace, ParkingType

ORDER_CHOICES = (
    ("no", "No"),
    ("parking_type", "駐車場タイプ"),
    ("room_no", "部屋番号"),
)


class ParkingSpaceFigForm(YearMonthForm):
    """空き駐車場配置図用Form"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["year"].widget.attrs["class"] = "input_form"
        self.fields["month"].widget.attrs["class"] = "select_form"


class ParkingSpaceListForm(YearMonthForm):
    """駐車場データのリスト表示用Form
    widgetをTextInputにすることでフィールド長さを調整できるが、IntegerFieldと
    しての増減ができなくなる。
    """

    parking_type = forms.ModelChoiceField(
        queryset=ParkingType.objects,
        empty_label="ALL",
        required=False,
        widget=forms.Select(attrs={"class": "select-css is-size-7"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["year"].widget.attrs["class"] = "input is-size-7"
        self.fields["month"].widget.attrs["class"] = "select-css is-size-7"


class MonthlyProcessingForm(forms.Form):
    """駐車場使用料金を前月と同じとして登録"""

    year = forms.IntegerField(label="年")
    month = forms.IntegerField(label="月")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["year"].widget.attrs["class"] = "input"
        self.fields["month"].widget.attrs["class"] = "input"


class ParkingUpdateForm(forms.ModelForm):
    """駐車場データの修正処理
    - parking_typeは固定なので、formフィールド非表示とする。
    - 駐車場Noはreadonly属性をTrueとする。
    """

    class Meta:
        model = ParkingSpace
        fields = (
            "no",
            "name",
            "room_number",
            "payment_date",
            "status_of_use",
            "comment",
        )
        widgets = {
            "no": forms.NumberInput(
                attrs={
                    "class": "input",
                    "readonly": True,
                }
            ),
            "name": forms.TextInput(
                attrs={
                    "class": "input",
                    "placeholder": "契約者名",
                }
            ),
            "room_number": forms.NumberInput(
                attrs={
                    "class": "input",
                }
            ),
            "payment_date": forms.DateInput(
                attrs={
                    "class": "input",
                    "readonly": True,
                }
            ),
            "status_of_use": forms.Select(
                attrs={
                    "class": "select-css",
                }
            ),
            "comment": forms.Textarea(
                attrs={
                    "class": "textarea",
                    "rows": "2",
                }
            ),
        }
        help_texts = {
            "room_number": "* 「空き」の場合は「0」にしてください。",
        }


class ParkingRirekiForm(forms.Form):
    """デフォルトは全データを表示
    widgetをTextInputにすることでフィールド長さを調整できるが、IntegerFieldと
    しての増減矢印が表示できなくなる。
    style属性で変更することはできた。
    year初期値はviewで設定する。
    """

    year = forms.IntegerField(
        label="西暦",
        widget=forms.NumberInput(attrs={"style": "width: 12ch"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["year"].widget.attrs["class"] = "input is-size-7"
        # self.fields['year'].initial = year
