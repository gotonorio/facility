from django import forms

from repair_plan.models import KoujiName


class RepairPlanCreateForm(forms.ModelForm):
    """長期修繕計画データ入力用form
    データ作成時には「通常工事」「大規模修繕工事」の２種類だけとするため、
    ローカルでKOUJI_KINDを宣言する。
    """

    DO_CALC = (
        (1, "計算対象"),
        (0, "対象外"),
    )
    version = forms.ModelChoiceField(
        label="計画バージョン",
        empty_label="選択してください",
        to_field_name="version",
        # queryset=MasterPlan.objects.all(),
        queryset=KoujiName.objects.all(),
        widget=forms.Select(attrs={"class": "select-css is-size-6"}),
    )
    do_calc = forms.ChoiceField(
        label="計算対象",
        choices=DO_CALC,
        widget=forms.Select(attrs={"class": "select-css"}),
        help_text="※ シミュレーション時に除外したい場合は「計算対象外」",
    )

    class Meta:
        """モデルフォームの場合はここで属性の変更をするのが一般的らしいが使いにくい
        Textareaの行数を指定したければ、ここで設定する。
        """

        model = KoujiName
        fields = (
            "version",
            "do_calc",
            "kouji_type",
            "kouji_name",
            "kouji_spec",
            "kouji_quantity",
            "unit",
            "unit_price",
            "kouji_year",
            "comment",
        )
        widgets = {
            "comment": forms.Textarea(
                attrs={
                    "placeholder": "markdown記法に対応しています。",
                    "rows": "3",
                    "required": False,
                }
            ),
            "kouji_quantity": forms.NumberInput(
                attrs={
                    "style": "width:10ch",
                }
            ),
        }
        required = {
            "complete": False,
        }

    def __init__(self, *args, **kwargs):
        """classはここで設定するのが楽。checkboxはcssで変更は不可能みたい"""
        super().__init__(*args, **kwargs)
        self.fields["kouji_type"].widget.attrs["class"] = "select-css"
        self.fields["kouji_name"].widget.attrs["class"] = "input"
        self.fields["kouji_spec"].widget.attrs["class"] = "input"
        self.fields["kouji_quantity"].widget.attrs["class"] = "input"
        self.fields["unit"].widget.attrs["class"] = "select-css"
        self.fields["unit_price"].widget.attrs["class"] = "input"
        self.fields["kouji_year"].widget.attrs["class"] = "input"
        self.fields["comment"].widget.attrs["class"] = "textarea"


class RepairPlanUpdateForm(forms.ModelForm):
    """修繕計画のUpdateForm
    工事実支出の登録もここで行う。
    """

    DO_CALC = (
        (1, "計算対象"),
        (0, "対象外"),
    )

    do_calc = forms.ChoiceField(
        label="計算対象",
        choices=DO_CALC,
        widget=forms.Select(attrs={"class": "select-css"}),
        help_text="※ シミュレーション時に除外したい場合は「計算対象外」",
    )

    class Meta:
        """actual_costを追加。"""

        model = KoujiName
        fields = (
            "do_calc",
            "kouji_type",
            "kouji_name",
            "kouji_spec",
            "kouji_quantity",
            "unit",
            "actual_cost",
            "unit_price",
            "kouji_year",
            "comment",
            "complete",
        )
        widgets = {
            "comment": forms.Textarea(
                attrs={
                    "placeholder": "markdown記法に対応しています。",
                    "rows": "3",
                    "required": False,
                }
            ),
            "kouji_quantity": forms.NumberInput(
                attrs={
                    "style": "width:10ch",
                }
            ),
            "complete": forms.CheckboxInput(),
        }
        required = {
            "complete": False,
        }

    def __init__(self, *args, **kwargs):
        """classはここで設定するのが楽。checkboxはcssで変更は不可能みたい"""
        super().__init__(*args, **kwargs)
        self.fields["kouji_type"].widget.attrs["class"] = "select-css"
        self.fields["kouji_name"].widget.attrs["class"] = "input"
        self.fields["kouji_spec"].widget.attrs["class"] = "input"
        self.fields["kouji_quantity"].widget.attrs["class"] = "input"
        self.fields["unit"].widget.attrs["class"] = "select-css"
        self.fields["unit_price"].widget.attrs["class"] = "input"
        self.fields["actual_cost"].widget.attrs["class"] = "input"
        self.fields["kouji_year"].widget.attrs["class"] = "input"
        self.fields["comment"].widget.attrs["class"] = "textarea"
