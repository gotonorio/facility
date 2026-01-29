from django import forms

from repair_plan.models import MasterKoujiType, MasterPlan, MasterUnit


class MasterPlanCreateForm(forms.ModelForm):
    class Meta:
        model = MasterPlan
        fields = (
            "version",
            "first_year",
            "final_year",
            "balance",
            "only_manager",
            "comment",
        )

    def __init__(self, *args, **kwargs):
        """classはここで設定するのが楽。checkboxはcssで変更は不可能みたい"""
        super().__init__(*args, **kwargs)
        self.fields["version"].widget.attrs["class"] = "input"
        self.fields["first_year"].widget.attrs["class"] = "input"
        self.fields["final_year"].widget.attrs["class"] = "input"
        self.fields["balance"].widget.attrs["class"] = "input"
        self.fields["comment"].widget.attrs["class"] = "textarea"


class MasterKoujiTypeForm(forms.ModelForm):
    class Meta:
        model = MasterKoujiType
        fields = ("sequense", "master_name", "live")


class MasterUnitForm(forms.ModelForm):
    class Meta:
        model = MasterUnit
        fields = ("unit_name",)


class DuplicateRepairPlanForm(forms.Form):
    """長期修繕計画の複製用Form"""

    source_ver = forms.ModelChoiceField(
        queryset=MasterPlan.objects.all().order_by("-version"),
        to_field_name="version",
        label="複製元 Ver.",
        widget=forms.Select(attrs={"class": "select-css"}),
    )

    new_ver = forms.IntegerField(
        label="新規バージョン番号",
        widget=forms.NumberInput(attrs={"class": "input"}),
    )

    def clean_new_ver(self):
        new_ver = self.cleaned_data["new_ver"]
        if MasterPlan.objects.filter(version=new_ver).exists():
            raise forms.ValidationError(f"Ver.{new_ver} は既に存在しています。")
        return new_ver
