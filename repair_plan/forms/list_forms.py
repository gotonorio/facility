import logging

from django import forms

from repair_plan.models import KoujiName, MasterKoujiType, MasterPlan

from .base import RepairPlanBaseForm

logger = logging.getLogger(__name__)


class RepairPlanListForm(RepairPlanBaseForm):
    koujitype = forms.ModelChoiceField(
        queryset=MasterKoujiType.objects.order_by("sequense"),
        label="工事種別",
        required=False,
        empty_label="工事種別全表示",
        widget=forms.Select(attrs={"class": "select-css is-size-6"}),
    )

    def __init__(self, is_manager, ver, *args, **kwargs):
        super().__init__(*args, **kwargs)
        qs = KoujiName.objects.all()
        if not is_manager:
            qs = qs.filter(version__only_manager=False)

        versions = qs.values_list("version__version", flat=True).order_by("-version").distinct()
        self.fields["version"].choices = [(v, v) for v in versions]

        if ver:
            self.initial["version"] = ver
        elif versions:
            self.initial["version"] = versions[0]


class DeleteKoujinameVerForm(RepairPlanBaseForm):
    """長期修繕計画の削除用Form"""

    confirm_flg = forms.BooleanField(label="削除確認", required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # KoujiNameに存在するMasterPlanのIDをリストとして取得
        existing_version_ids = KoujiName.objects.values_list("version", flat=True).distinct()

        # 親クラスの version フィールドの queryset を直接書き換える
        # これにより、バリデーションもこのQuerySetに基づいて行われます
        self.fields["version"].queryset = MasterPlan.objects.filter(id__in=existing_version_ids).order_by(
            "-version"
        )
