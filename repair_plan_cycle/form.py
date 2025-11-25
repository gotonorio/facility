import logging

from django import forms
from django.core.exceptions import ValidationError
from repair_plan.models import KoujiName, MasterPlan

from repair_plan_cycle.models import KoujiCycleData

logger = logging.getLogger(__name__)


class CycleDataListForm(forms.Form):
    """工事周期データ選択用Form"""

    version = forms.ModelChoiceField(
        queryset=KoujiCycleData.objects.values_list("version", flat=True).distinct().order_by("-version"),
        label="計画 Ver.",
        empty_label="選択してください",
        required=True,
        widget=forms.Select(attrs={"class": "select-css is-size-7"}),
    )


class CycleDataForm(forms.ModelForm):
    """工事周期データ用Form"""

    version = forms.ModelChoiceField(
        label="計画バージョン",
        empty_label="選択してください",
        to_field_name="version",
        queryset=MasterPlan.objects.all(),
        widget=forms.Select(attrs={"class": "select-css is-size-6"}),
    )

    # ModelFormの場合にはMetaクラスが必要。Formクラスでは使用できない
    class Meta:
        model = KoujiCycleData
        fields = [
            "version",
            "kouji_type",
            "kouji_name",
            "first_year",
            "repeat_cycle",
            "cost",
            "comment",
        ]

    def __init__(self, *args, **kwargs):
        """classはここで設定するのが楽。checkboxはcssで変更は不可能みたい"""
        super().__init__(*args, **kwargs)
        # self.fields["version"].widget.attrs["class"] = "select-css"
        self.fields["kouji_type"].widget.attrs["class"] = "select-css"
        self.fields["kouji_name"].widget.attrs["class"] = "input"
        self.fields["first_year"].widget.attrs["class"] = "input"
        self.fields["repeat_cycle"].widget.attrs["class"] = "input"
        self.fields["cost"].widget.attrs["class"] = "input"
        self.fields["comment"].widget.attrs["class"] = "textarea"
        self.fields["comment"].widget.attrs["rows"] = 2


class RepairPlanCreateForm(forms.Form):
    """修繕計画変換用Form"""

    version = forms.ChoiceField(
        choices=[
            (v, v)
            for v in KoujiCycleData.objects.values_list("version", flat=True).distinct().order_by("-version")
        ],
        label="計画 Ver.",
        required=True,
    )
    start_year = forms.IntegerField(
        label="開始年度",
        required=True,
    )
    last_year = forms.IntegerField(
        label="終了年度",
        required=True,
    )

    def __init__(self, *args, **kwargs):
        """classはここで設定するのが楽。checkboxはcssで変更は不可能みたい"""
        super().__init__(*args, **kwargs)
        self.fields["version"].widget.attrs["class"] = "select-css"
        self.fields["start_year"].widget.attrs["class"] = "input"
        self.fields["last_year"].widget.attrs["class"] = "input"
        self.fields["start_year"].widget.attrs["style"] = "width: 160px;"
        self.fields["last_year"].widget.attrs["style"] = "width: 160px;"

    def clean_version(self):
        # ChoiceField は文字列を返すので int に変換
        version = int(self.cleaned_data["version"])
        if KoujiName.objects.filter(version__version=version).exists():
            logger.warning(f"バージョン番号 {version} は既に存在しています")
            raise ValidationError(f"バージョン番号 {version} は既に存在しています")
        return version


class CycleDataDuplicateForm(forms.Form):
    """工事周期データの複製フォーム"""

    # 複製元 version
    source_version = forms.ChoiceField(
        label="複製元 Version",
        widget=forms.Select(attrs={"class": "select-css"}),
        required=True,
    )

    # 新しい version
    new_version = forms.IntegerField(
        label="新規 Version",
        widget=forms.NumberInput(attrs={"class": "input"}),
        required=True,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # BasicPlanData に存在する version の一覧を取得し ChoiceField にセット
        versions = (
            KoujiCycleData.objects.all().order_by("-version").values_list("version", flat=True).distinct()
        )

        self.fields["source_version"].choices = [(v, v) for v in versions]


class CycleDataDeleteForm(forms.Form):
    """工事周期データの削除用Form"""

    delete_version = forms.ChoiceField(
        choices=[
            (v, v)
            for v in KoujiCycleData.objects.values_list("version", flat=True).distinct().order_by("-version")
        ],
        label="削除するVer.",
        required=True,
        widget=forms.Select(attrs={"class": "select-css is-size-7"}),
    )

    confirm_flg = forms.NullBooleanField(
        label="削除確認.",
        initial=False,
        widget=forms.NullBooleanSelect(
            attrs={"class": "select-css"},
        ),
    )
