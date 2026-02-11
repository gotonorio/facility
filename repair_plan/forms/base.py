from django import forms

from repair_plan.models import MasterPlan


class RepairPlanBaseForm(forms.Form):
    """修繕計画表示用のベースForm
    - widgetは継承先で設定する
    """

    version = forms.ModelChoiceField(
        queryset=MasterPlan.objects.none(),
        label="計画 Ver.",
        required=True,
        # widget=forms.Select(
        #     attrs={
        #         "style": "width:10ch",
        #         "class": "select",
        #     }
        # ),
    )
