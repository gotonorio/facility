from django import forms
from facility.forms import YearMonthForm

from motorcycle.models import MotorCycleSpace


class MotorCycleSpaseListForm(YearMonthForm):
    """駐輪場一覧表示用Form"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["year"].widget.attrs["class"] = "input is-size-7"
        self.fields["month"].widget.attrs["class"] = "select-css is-size-7"


class MotorCycleUpdateForm(forms.ModelForm):
    """バイク置場データの修正処理"""

    class Meta:
        model = MotorCycleSpace
        fields = ("no", "room_no", "date", "status_of_use", "comment")
        widgets = {
            "no": forms.NumberInput(
                attrs={
                    "class": "input",
                    "readonly": True,
                }
            ),
            "room_no": forms.NumberInput(
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
            "room_no": "* 「空き」の場合は「0」にしてください。",
        }


class MonthlyProcessingForm(forms.Form):
    """駐車場使用料金を前月と同じとして登録"""

    year = forms.IntegerField(label="年")
    month = forms.IntegerField(label="月")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["year"].widget.attrs["class"] = "input"
        self.fields["month"].widget.attrs["class"] = "input"
