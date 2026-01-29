from django import forms

# from common.forms.base_form import YearMonthForm
from motorcycle.models import MotorCycleSpace


class MotorCycleUpdateForm(forms.ModelForm):
    """バイク置場データの修正処理"""

    def clean(self):
        cleaned_data = super().clean()
        no = cleaned_data.get("no")
        room = cleaned_data.get("room_no")
        status = cleaned_data.get("status_of_use")

        # room_noはint型として扱う（Viewのint変換ロジックを吸収）
        try:
            room_val = int(room) if room is not None else 0
        except ValueError:
            room_val = 0

        if room_val == 0 and status != "空き":
            raise forms.ValidationError(
                f"バイク置場 No.{no}の部屋番号が「0」なら使用状況は「空き」にしてください。"
            )

        if status == "空き" and room_val > 0:
            raise forms.ValidationError(
                f"バイク置場 No.{no}の使用状況が「空き」なら部屋番号は「0」にしてください。"
            )

        return cleaned_data

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
