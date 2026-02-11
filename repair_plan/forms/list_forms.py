import logging

from django import forms

from repair_plan.models import KoujiName, MasterKoujiType, MasterPlan

from .base import RepairPlanBaseForm

logger = logging.getLogger(__name__)


class RepairPlanListForm(RepairPlanBaseForm):
    """長期修繕工事リスト表示用Form"""

    koujitype = forms.ModelChoiceField(
        queryset=MasterKoujiType.objects.order_by("sequense"),
        label="工事種別",
        required=False,
        empty_label="工事種別全表示",
        # bulmaの select クラスを適用する場合は、DjangoではなくHTMLテンプレート側で指定すること
        # widget=forms.Select(attrs={"class": "select"}),  # Bulma CSS framework
    )

    def __init__(self, *args, **kwargs):
        # 1. super().__init__ の前に追加引数を pop する
        is_manager = kwargs.pop("is_manager", False)
        ver = kwargs.pop("ver", None)

        # 2. 親クラスを初期化（ここで self.fields が作成される）
        super().__init__(*args, **kwargs)

        # 3. 取り出した値を使ってロジックを実行
        qs = KoujiName.objects.all()
        if not is_manager:
            qs = qs.filter(version__only_manager=False)

        versions = (
            qs.values_list("version__version", flat=True)
            .order_by("-version")
            .distinct()
        )
        self.fields["version"].choices = [(v, v) for v in versions]

        # 初期値のセット
        if ver:
            # ver がオブジェクトならその version 数値を使う（__str__の実装に合わせて調整）
            self.initial["version"] = str(ver)
        elif versions:
            self.initial["version"] = versions[0]

        # widget
        self.fields["version"].widget.attrs["class"] = "select is-size-7"


class DeleteKoujinameVerForm(RepairPlanBaseForm):
    """長期修繕計画の削除用Form"""

    confirm_flg = forms.BooleanField(
        label="削除確認",
        required=False,
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # KoujiNameに存在するMasterPlanのIDをリストとして取得
        existing_version_ids = KoujiName.objects.values_list(
            "version", flat=True
        ).distinct()

        # 親クラスの version フィールドの queryset を直接書き換える
        # これにより、バリデーションもこのQuerySetに基づいて行われます
        self.fields["version"].queryset = MasterPlan.objects.filter(
            id__in=existing_version_ids
        ).order_by("-version")

        self.fields["version"].widget.attrs["class"] = "select-css"