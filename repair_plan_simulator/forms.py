import logging

from django import forms

from repair_plan.models import KoujiName, MasterPlan
from repair_plan_simulator.models import ConsumerPriceIndex, Shuuzenhi_income

logger = logging.getLogger(__name__)


class SimulateDataForm(forms.Form):
    """修繕計画シミュレーション画面でのForm"""

    masterplan_ver = forms.ModelChoiceField(
        queryset=MasterPlan.objects.none(),
        label="計画 Ver.",
        required=True,
        widget=forms.Select(attrs={"class": "select-css is-size-6"}),
    )
    # 経費率
    expense_rate = forms.FloatField(
        label="経費率(%)",
        initial=10.0,
        widget=forms.NumberInput(attrs={"class": "input"}),
    )
    # 消費税率
    sales_tax_rate = forms.FloatField(
        label="消費税率(%)",
        initial=10.0,
        widget=forms.NumberInput(attrs={"class": "input"}),
    )
    # 修繕費収入率
    shuuzenhi_rate = forms.FloatField(
        label="修繕費収入率",
        initial=1.0,
        widget=forms.NumberInput(attrs={"class": "input"}),
    )
    # 駐車場収入率
    parking_rate = forms.FloatField(
        label="駐車場収入率",
        initial=1.0,
        widget=forms.NumberInput(attrs={"class": "input"}),
    )
    # 物価指数考慮
    cpi_flg = forms.BooleanField(
        label="物価指数を考慮",
        required=False,
    )
    # 完了工事を考慮するかどうか
    include_actual_cost = forms.BooleanField(
        label="完了工事を考慮",
        required=False,
    )

    def __init__(self, *args, **kwargs):
        """
        forms.Formの定義時に initial=Model.objects.get(...) のように DBに即時アクセスすると、
        migrate時にDBが存在しないためエラーが発生する。--> 遅延評価するため__init__()で処理する。
        only_managerがFalseなら、verの初期値は設定しない。
        """
        # ビューから渡された引数を取り出す（親クラスに渡す前に消す必要がある）
        self.is_manager = kwargs.pop("is_manager", False)
        super(SimulateDataForm, self).__init__(*args, **kwargs)
        try:
            if self.is_manager:
                # 管理者には全ての修繕計画versionを表示。
                versions = (
                    KoujiName.objects.values_list("version__version", flat=True)
                    .order_by("-version")
                    .distinct()
                )
                self.fields["masterplan_ver"].choices = [(v, v) for v in versions]
            else:
                # 管理者以外にはonly_managerフラグがFalseの修繕計画versionを表示。
                versions = (
                    KoujiName.objects.filter(version__only_manager=False)
                    .values_list("version__version", flat=True)
                    .order_by("-version")
                    .distinct()
                )
                self.fields["masterplan_ver"].choices = [(v, v) for v in versions]
        except Exception as e:
            # DB未マイグレート or モデルが空の時でもエラーにしない
            logger.error(f"RepairPlanListForm init error: {e}")
            self.fields["masterplan_ver"].choices = []

        # cpi_flgの初期値をTrueに設定
        self.fields["cpi_flg"].initial = True


class ShuuzenhiIncomeCreateForm(forms.ModelForm):
    """計画初年度からの修繕費会計の収入額を登録
    駐車場会計を独立させたので、機械式駐車機保守費を考えない。
    """

    class Meta:
        model = Shuuzenhi_income
        fields = ("year", "income", "parking_income", "extra_income", "real", "comment")
        labels = {
            "year": "西暦",
            "income": "修繕積立金額",
            "parking_income": "駐車場会計より",
            "extra_income": "その他収入",
            "real": "実収入",
        }
        widgets = {
            "year": forms.NumberInput(
                attrs={
                    "class": "input",
                }
            ),
            "income": forms.NumberInput(
                attrs={
                    "class": "input",
                }
            ),
            "parking_income": forms.NumberInput(
                attrs={
                    "class": "input",
                }
            ),
            "extra_income": forms.NumberInput(
                attrs={
                    "class": "input",
                }
            ),
            "real": forms.NullBooleanSelect(
                attrs={
                    "class": "select-css",
                }
            ),
            "comment": forms.Textarea(
                attrs={"class": "textarea", "rows": "4", "required": False}
            ),
            # "comment": forms.TextInput(
            #     attrs={
            #         "class": "input",
            #     }
            # ),
        }


class CPICreateForm(forms.ModelForm):
    """物価指数登録Form"""

    # 以降の年について毎年同じ物価上昇率を考慮
    continuas = forms.BooleanField(
        required=False,
        label="連続入力",
        help_text="※ 修正時、以降の年について毎年同じ物価上昇率を考慮する。",
    )

    class Meta:
        model = ConsumerPriceIndex
        fields = ("year", "cpi", "comment")
        labels = {
            "year": "西暦",
            "cpi": "物価指数",
            "comment": "コメント",
        }
        widgets = {
            "year": forms.NumberInput(
                attrs={
                    "class": "input",
                }
            ),
            "cpi": forms.NumberInput(
                attrs={
                    "class": "input",
                }
            ),
            "comment": forms.Textarea(
                attrs={"class": "textarea", "rows": "4", "required": False}
            ),
        }

    # 入力フォームの初期値を設定するため
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["cpi"].initial = "1.000"
