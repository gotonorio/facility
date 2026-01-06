from django import forms
from facility.forms import YearMonthForm

from bicycle.models import LOCATION, BicycleSpace


class BicycleSpaseListForm(YearMonthForm):
    """駐輪場一覧表示用Form"""

    location = forms.ChoiceField(
        label="場所",
        widget=forms.Select(
            attrs={
                "class": "select-css is-size-7",
                "style": "width:10ch",
            }
        ),
        choices=LOCATION,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["year"].widget.attrs["class"] = "input is-size-7"
        self.fields["month"].widget.attrs["class"] = "select-css is-size-7"


class BicycleUpdateForm(forms.ModelForm):
    """駐輪場データの修正処理"""

    def clean(self):
        cleaned_data = super().clean()
        no = cleaned_data.get("no")
        room = cleaned_data.get("room_number")
        status = cleaned_data.get("status_of_use")

        # 整合性チェック
        if room == 0 and status != "空き":
            raise forms.ValidationError(
                f"駐輪場 No.{no}の部屋番号が「0」なら使用状況は「空き」にしてください。"
            )

        if status == "空き" and room > 0:
            raise forms.ValidationError(
                f"駐輪場 No.{no}の使用状況が「空き」なら部屋番号は「0」にしてください。"
            )

        return cleaned_data

    class Meta:
        model = BicycleSpace
        fields = ("no", "location", "room_number", "date", "status_of_use", "comment")
        widgets = {
            "no": forms.NumberInput(
                attrs={
                    "class": "input",
                    "readonly": True,
                }
            ),
            "location": forms.Select(
                attrs={
                    "class": "select-css",
                }
            ),
            "room_number": forms.NumberInput(
                attrs={
                    "class": "input",
                }
            ),
            "date": forms.DateInput(
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


class MonthlyProcessingForm(forms.Form):
    """駐車場使用料金を前月と同じとして登録"""

    year = forms.IntegerField(label="年")
    month = forms.IntegerField(label="月")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["year"].widget.attrs["class"] = "input"
        self.fields["month"].widget.attrs["class"] = "input"
