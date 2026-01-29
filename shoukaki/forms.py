from django import forms
from django.utils import timezone

from .models import Shoukaki, ShoukakiType

ORDER_CHOICES = (
    ("0", "No"),
    ("製造年", "製造年順"),
    ("設置日", "設置日順"),
    ("点検日", "点検日順"),
    ("形式", "形式順"),
)


class ShoukakiTypeForm(forms.ModelForm):
    """消火器種別データ入力用Form"""

    class Meta:
        model = ShoukakiType
        fields = [
            "name",
            "shoukaki_type",
            "keisiki",
            "maker",
            "valid_period",
            "price",
            "alive",
        ]

    def __init__(self, *args, **kwargs):
        super(ShoukakiTypeForm, self).__init__(*args, **kwargs)
        self.fields["name"].widget.attrs["class"] = "input"
        self.fields["shoukaki_type"].widget.attrs["class"] = "input"
        self.fields["keisiki"].widget.attrs["class"] = "input"
        self.fields["maker"].widget.attrs["class"] = "input"
        self.fields["valid_period"].widget.attrs["class"] = "input"
        self.fields["price"].widget.attrs["class"] = "input"


class ShoukakiForm(forms.ModelForm):
    """消火器データ入力用form"""

    shoukaki = forms.ModelChoiceField(
        label="消火器種類",
        queryset=ShoukakiType.objects.filter(alive=True),
        widget=forms.Select(
            attrs={
                "class": "select-css",
            }
        ),
    )
    alive = forms.NullBooleanField(
        label="有効",
        widget=forms.NullBooleanSelect(
            attrs={
                "class": "select-css",
            }
        ),
    )

    class Meta:
        model = Shoukaki
        fields = [
            "code",
            "shoukaki",
            "location",
            "installation_date",
            "inspection_date",
            "made_year",
            "made_no",
            "comment",
            "alive",
        ]
        widgets = {
            "installation_date": forms.DateInput(
                attrs={
                    "type": "date",
                    "value": timezone.datetime.now().strftime("%Y-%m-%d"),
                    "class": "is-size-6",
                }
            ),
            "inspection_date": forms.DateInput(
                attrs={
                    "type": "date",
                    "value": timezone.datetime.now().strftime("%Y-%m-%d"),
                    "class": "is-size-6",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        """フィールドにclassを設定する"""
        super(ShoukakiForm, self).__init__(*args, **kwargs)
        self.fields["code"].widget.attrs["class"] = "input"
        self.fields["location"].widget.attrs["class"] = "input"
        self.fields["made_year"].widget.attrs["class"] = "input"
        self.fields["made_no"].widget.attrs["class"] = "input"
        self.fields["comment"].widget.attrs["class"] = "text"


class ShoukakiListForm(forms.Form):
    """消火器リストのデータ選択用Form"""

    order = forms.ChoiceField(
        label="表示順：",
        # bulmaの select クラスを適用する場合は、DjangoではなくHTMLテンプレート側で指定する
        # widget=forms.Select(attrs={"class": "select is-small"}),
        choices=ORDER_CHOICES,
    )


class ShoukakiDisposalForm(forms.Form):
    """廃棄消火器リストの選択用"""

    year = forms.IntegerField(
        label="年度",
        widget=forms.NumberInput(attrs={"style": "width: 12ch"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["year"].widget.attrs["class"] = "input is-size-7"
