import csv
import io
import logging

from django import forms

from repair_plan.models import KoujiName, MasterKoujiType, MasterPlan, MasterUnit

logger = logging.getLogger(__name__)


# ----------------------------------------------------------------------------
# forms.Form
# ----------------------------------------------------------------------------
class RepairPlanBaseForm(forms.Form):
    """修繕計画表示用のベースForm"""

    version = forms.ModelChoiceField(
        # ダミーのqueryset。必要なquerysetは継承クラスのinit__()でグループにより表示を変える。
        queryset=MasterPlan.objects.none(),
        label="計画 Ver.",
        required=True,
        widget=forms.Select(attrs={"class": "select-css is-size-7"}),
    )


class RepairPlanListForm(RepairPlanBaseForm):
    """修繕計画一覧表示フォーム
    http://www.subthread.co.jp/blog/20160531/
    """

    koujitype = forms.ModelChoiceField(
        queryset=MasterKoujiType.objects.order_by("sequense"),
        label="工事種別",
        empty_label="工事種別全表示",
        error_messages={
            "required": "You didn't select a choice.",
            "invalid_choice": "invalid choice.",
        },
        required=False,
        initial="ALL",
        widget=forms.Select(attrs={"class": "select-css is-size-7"}),
    )

    def __init__(self, is_manager, *args, **kwargs):
        """viewがら渡されたis_managerフラグでquerysetを変更させる
        querysetはversionのリストを表示させる。
        forms.Formの定義時に initial=Model.objects.get(...) のように DBに即時アクセスすると、
        migrate時にDBが存在しないためエラーが発生する。--> 遅延評価するため__init__()で処理する。
        only_maagerがFalseなら、verの初期値は設定しない。
        """
        super(RepairPlanListForm, self).__init__(*args, **kwargs)
        try:
            if is_manager:
                # 管理者には全ての修繕計画versionを表示。
                versions = (
                    KoujiName.objects.values_list("version__version", flat=True)
                    .order_by("-version")
                    .distinct()
                )
                self.fields["version"].choices = [(v, v) for v in versions]
            else:
                # 管理者以外にはonly_managerフラグがFalseの修繕計画versionを表示。
                versions = (
                    KoujiName.objects.filter(version__only_manager=False)
                    .values_list("version__version", flat=True)
                    .order_by("-version")
                    .distinct()
                )
                self.fields["version"].choices = [(v, v) for v in versions]
        except Exception as e:
            logger.error(f"RepairPlanListForm init error: {e}")
            self.fields["keikaku_ver"].choices = []

        # --------------------------
        # ★ 最大 version を初期値に設定
        # --------------------------
        if versions:
            max_version = versions[0]  # order_by('-version') のため先頭が最大
            self.initial["keikaku_ver"] = max_version


class RepairPlanTableForm(RepairPlanBaseForm):
    """修繕計画表用Form
    http://www.subthread.co.jp/blog/20160531/
    """

    def __init__(self, is_manager, *args, **kwargs):
        """viewがら渡されたonly_managerフラグでquerysetを変更させる
        - querysetはversionのリストを表示させる。
        """
        super(RepairPlanTableForm, self).__init__(*args, **kwargs)

        if is_manager:
            # 管理者には全ての修繕計画versionを表示。
            versions = (
                KoujiName.objects.values_list("version__version", flat=True).order_by("-version").distinct()
            )
            self.fields["version"].choices = [(v, v) for v in versions]
        else:
            # 管理者以外にはonly_managerフラグがFalseの修繕計画versionを表示。
            versions = (
                KoujiName.objects.filter(version__only_manager=False)
                .values_list("version__version", flat=True)
                .order_by("-version")
                .distinct()
            )
            self.fields["version"].choices = [(v, v) for v in versions]

        # --------------------------
        # ★ 最大 version を初期値に設定
        # --------------------------
        if versions:
            max_version = versions[0]  # order_by('-version') のため先頭が最大
            self.initial["keikaku_ver"] = max_version


class DuplicateRepairPlanForm(forms.ModelForm):
    """長期修繕計画の複製用Form
    - ModelFormを使ってMasterPlanモデルと連携する。
    - to_field_nameを使ってversionフィールドを表示キーにする。
    参考：https://docs.djangoproject.com/en/6.0/ref/forms/fields/#django.forms.ModelChoiceField.to_field_name
    """

    # new_ver は MasterPlan にないので追加フィールド
    new_ver = forms.IntegerField(
        label="新規バージョン番号", widget=forms.NumberInput(attrs={"class": "input"})
    )

    # 複製元バージョン
    source_ver = forms.ModelChoiceField(
        queryset=MasterPlan.objects.all().order_by("-version"),
        to_field_name="version",  # version を表示キーにしてMasterPlanオブジェクトを取得できる
        label="複製元 Ver.",
        widget=forms.Select(attrs={"class": "select-css"}),
    )

    class Meta:
        model = MasterPlan
        fields = ("new_ver", "source_ver")  # ModelFormなのでMetaに必要


class ImportRepairPlanDataForm(forms.Form):
    """長期修繕計画データのインポート用フォーム
    https://blog.narito.ninja/detail/60
    """

    file = forms.FileField(
        label="CSVファイル",
        help_text="※ 文字コードはutf-8です。",
    )

    # BulmaがFileFieldの選択ボタンに未対応？
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["file"].widget.attrs["class"] = "is-size-6"

    # fileフィールドがあればclean_file()が自動的に呼ばれる。
    # ここで自前のチェックとデータの読み込みを行い、views.pyのform_valid()で保存する。
    # https://stackoverflow.com/questions/16368993/how-to-validate-contents-of-a-csv-file-using-django-forms
    def clean_file(self):
        file = self.cleaned_data["file"]
        # (1) ファイル名のチェック。
        if not file.name.endswith(".csv"):
            raise forms.ValidationError("拡張子がcsvのファイルをアップロードしてください")
        # (2) ファイルの中身をチェックするため、読み込みをここで行う。
        csvfile = io.TextIOWrapper(file, encoding="utf-8")
        reader = csv.reader(csvfile)

        # 各行から作ったモデルインスタンスを保管するリスト
        self._instances = []
        # 1データは9項目から構成されている
        number_of_columns = 9
        try:
            # enumerateを使って読み込んだ行番号を取得する。
            for i, row in enumerate(reader):
                # (1) 先頭行でヘッダーの存在をチェック。
                if str(row[0]).isdecimal and str(row[1]).isdecimal and str(row[6]).isdecimal:
                    pass
                else:
                    raise forms.ValidationError("ヘッダーは削除してください")
                # (2) 先頭行でMastePlanオブジェクトを取得する。
                if i == 0:
                    try:
                        ver_object = MasterPlan.objects.get(version=row[0])
                    except MasterPlan.DoesNotExist:
                        raise forms.ValidationError(
                            f"バージョン番号 {row[0]} は「修繕計画マスタ」に登録されていません!"
                        )
                # (3) 列数をチェックする。
                if len(row) != number_of_columns:
                    raise forms.ValidationError(
                        f"{i + 1}行目が不正です。本来の列数:{number_of_columns} \
                        {i + 1}行目の列数:{len(row)}"
                    )
                # (4) 修繕計画マスタのversion番号をチェックする。
                chk_version = KoujiName.objects.filter(version__version=row[0])
                if len(chk_version) > 0:
                    raise forms.ValidationError(f"バージョン番号{row[0]}は、既に存在しています")
                # (5) 「予算」「実支出」で数字のカンマがあれば削除する。
                if row[6].find(",") > 0:
                    row[6] = int(row[6].replace(",", ""))
                if row[7].find(",") > 0:
                    row[7] = int(row[7].replace(",", ""))
                # (6) 工事種別名のチェック
                try:
                    _ = MasterKoujiType.objects.get(master_name=row[2])
                except MasterKoujiType.DoesNotExist:
                    raise forms.ValidationError(
                        f"{i + 1}行目の{row[2]} は工事種別マスタが登録されていません!"
                    )
                # (7) 施工単位名のチェック
                try:
                    _ = MasterUnit.objects.get(unit_name=row[5])
                except MasterUnit.DoesNotExist:
                    raise forms.ValidationError(
                        f"{i + 1}行目の{row[5]} は施工単位マスタが登録されていません!"
                    )
                # (8) 実支出金額のチェック
                if str(row[7]) == "":
                    row[7] = 0
                #     pass
                # else:
                #     raise forms.ValidationError(f"実支出額{row[7]}がない場合は0が必要です")

                koujiname = KoujiName(
                    version=ver_object,
                    kouji_year=row[1],
                    kouji_type=MasterKoujiType.objects.get(master_name=row[2]),
                    kouji_name=row[3],
                    # kouji_spec=row[4],
                    kouji_quantity=row[4],
                    unit=MasterUnit.objects.get(unit_name=row[5]),
                    unit_price=row[6],
                    actual_cost=row[7],
                    comment=row[8],
                    do_calc=1,
                )
                self._instances.append(koujiname)
        except UnicodeDecodeError:
            raise forms.ValidationError("データを確認するか、管理者に連絡してください。")
        return file

    def save(self):
        """clean_fileで作成したモデルインスタンスのリストを使って保存処理する
        - 呼び出しはdata_views.pyのImportRepairPlanDataViewから行う。
        """
        for koujiname in self._instances:
            # オブジェクトのsave関数を呼び出す。
            koujiname.save()


class DeleteKoujinameVerForm(forms.Form):
    """削除する工事計画Version用Form"""

    keikaku_ver = forms.ModelChoiceField(
        queryset=MasterPlan.objects.all(),
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


# ----------------------------------------------------------------------------
# forms.ModelForm
# ----------------------------------------------------------------------------
class MasterPlanCreateForm(forms.ModelForm):
    """MasterPlan登録用フォーム
    各バージョンの概要、初期値を定義する。
    """

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
        labels = {
            "version": "計画バージョン",
            "first_year": "計画初年度",
            "final_year": "計画最終年度",
            "balance": "初年度資産額",
            "only_manager": "管理者専用",
            "comment": "説明",
        }
        widgets = {
            "version": forms.NumberInput(
                attrs={
                    "class": "input",
                }
            ),
            "first_year": forms.NumberInput(
                attrs={
                    "class": "input",
                }
            ),
            "final_year": forms.NumberInput(
                attrs={
                    "class": "input",
                }
            ),
            "balance": forms.TextInput(
                attrs={
                    "class": "input",
                }
            ),
            "only_manager": forms.NullBooleanSelect(
                attrs={
                    "class": "select-css",
                }
            ),
            "comment": forms.Textarea(attrs={"class": "textarea", "rows": "4", "required": False}),
        }


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
        queryset=MasterPlan.objects.all(),
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


class MasterKoujiTypeForm(forms.ModelForm):
    """工事種別マスターの登録用フォーム"""

    sequense = forms.IntegerField(label="表示順序")
    master_name = forms.CharField(label="工事種別名", max_length=256)
    live = forms.BooleanField(label="有効/無効", required=False)

    class Meta:
        model = MasterKoujiType
        fields = ("sequense", "master_name", "live")

    # fieldにclassを設定する。
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["sequense"].widget.attrs["class"] = "input"
        self.fields["master_name"].widget.attrs["class"] = "input"
        self.fields["live"].widget.attrs["class"] = ""


class MasterUnitForm(forms.ModelForm):
    """数量単位マスターの登録用フォーム"""

    unit_name = forms.CharField(label="数量単位名", max_length=16)

    class Meta:
        model = MasterUnit
        fields = ("unit_name",)

    # fieldにclassを設定する。
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["unit_name"].widget.attrs["class"] = "input"
