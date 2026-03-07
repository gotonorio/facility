from common.forms.base_form import YearMonthForm
from django import forms

from parking.models import ParkingSpace

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

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get("name")
        room = cleaned_data.get("room_number", 0)
        status = cleaned_data.get("status_of_use")
        no = cleaned_data.get("no")

        # 整合性チェック
        if room == 0 and status not in ["空き", "使用中止"]:
            raise forms.ValidationError(f"駐車場 No.{no}の「部屋番号」を入力してください。")

        if name is None and status not in ["空き", "使用中止"]:
            raise forms.ValidationError(f"駐車場 No.{no}の「契約者」を入力してください。")

        if status == "空き" and room > 0:
            raise forms.ValidationError(f"使用状況が「空き」なら部屋番号{room}は0にしてください。")

        if status == "空き" and name is not None:
            raise forms.ValidationError("使用状況が「空き」なら契約者は「空白」にしてください。")

        return cleaned_data

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
            "no": forms.NumberInput(attrs={"class": "input", "readonly": True, "style": "width: 12ch"}),
            "name": forms.TextInput(
                attrs={
                    "class": "input",
                    "placeholder": "契約者名",
                    "style": "width: 24ch",
                },
            ),
            "room_number": forms.NumberInput(attrs={"class": "input", "style": "width: 12ch"}),
            "payment_date": forms.DateInput(
                attrs={"class": "input", "readonly": True, "style": "width: 16ch"}
            ),
            "status_of_use": forms.Select(attrs={"class": "select-css"}),
            "comment": forms.Textarea(attrs={"class": "textarea", "rows": "2"}),
        }
        help_texts = {
            "room_number": "* 「空き」の場合は「0」にしてください。",
        }
