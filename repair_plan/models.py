import logging

from django.db import models
from django.db.models import F, IntegerField
from django.db.models.aggregates import Case, Max, Min, Sum, When

logger = logging.getLogger(__name__)


class MasterPlan(models.Model):
    """修繕計画マスター"""

    version = models.IntegerField(verbose_name="Ver")
    first_year = models.IntegerField(verbose_name="計画初年度")
    final_year = models.IntegerField(verbose_name="計画最終年度", default=0)
    balance = models.BigIntegerField(verbose_name="初年度修繕資産")

    # 管理者のシミュレーション用データ
    only_manager = models.BooleanField(verbose_name="管理者専用", default=False)
    only_specialist = models.BooleanField(verbose_name="専門委員専用", default=False)
    comment = models.TextField(verbose_name="説明", blank=True, null=True)

    def __int__(self):
        return self.version

    def __str__(self):
        return str(self.version)


class MasterKoujiType(models.Model):
    """工事種別マスター"""

    sequense = models.IntegerField(verbose_name="表示順序")
    master_name = models.CharField(verbose_name="工事種別", max_length=128)
    live = models.BooleanField(default=True)

    def __str__(self):
        return self.master_name


class MasterUnit(models.Model):
    """数量単位"""

    unit_name = models.CharField(verbose_name="単位", max_length=32)

    def __str__(self):
        return self.unit_name


class KoujiNameQuerySet(models.QuerySet):
    """KoujiNameのQuerySet"""

    def get_year_range(self, ver):
        """修繕計画の開始、終了年を返す"""
        year_range = self.filter(version__version=ver).aggregate(
            end_year=Max("kouji_year"), start_year=Min("kouji_year")
        )
        return year_range

    def get_koujiname_list(self, ver, koujitype):
        """指定されたバージョンの計画工抽出querysetを返す"""
        # クエリの作成
        qs = self.select_related("kouji_type")
        if koujitype == "ALL":
            qs = qs.filter(version__version=ver)
        else:
            qs = qs.filter(version__version=ver).filter(kouji_type=koujitype)
        return qs

    def delete_koujiname_by_ver(self, ver):
        """指定されたバージョンのkoujinameを削除する"""
        try:
            qs = self.filter(version__version=ver)
        except self.DoesNotExist:
            msg = f"version={ver}が存在しません"
            return msg
        qs.delete()
        msg = f"version{ver}を削除しました"
        return msg

    def get_repair_plan_list(self, ver, start_year, end_year, simple=False):
        """長期繕計画表を返す
        - ver: バージョン番号
        - start_year: 開始年
        - end_year: 終了年
        - simple: Trueの場合は工事種別名のみ、Falseの場合は工事名も含める
        - 表示年数（列数）を動的に決めるためlistとして返す(values_list)
        """
        if simple:
            qs = self.filter(version__version=ver).values_list("kouji_type__master_name")
        else:
            qs = self.filter(version__version=ver).values_list("kouji_type__master_name", "kouji_name")

        cnt = end_year - start_year + 1
        # annotateの引数をDictとして生成する。
        annotations = {}
        for i in range(0, cnt):
            annotations[f"y{i + 1}"] = Sum(
                Case(
                    When(
                        kouji_year=start_year + i,
                        then=F("kouji_quantity") * F("unit_price"),
                    ),
                    output_field=IntegerField(),
                    default=0,
                ),
            )
        annotations["total"] = Sum(
            Case(
                When(
                    version__version=ver,
                    then=F("kouji_quantity") * F("unit_price"),
                ),
                output_field=IntegerField(),
                default=0,
            ),
        )
        # annotate引数はDictとして動的に生成して設定することができる。
        if simple:
            qs = qs.annotate(**annotations).order_by("kouji_type__master_name")
        else:
            qs = qs.annotate(**annotations).order_by("kouji_type", "kouji_name")
        return qs

    def get_repair_plan_list_by_year(self, ver, year):
        """指定された年の修繕計画を返す"""
        qs = self.filter(version__version=ver, kouji_year=year)
        return qs


class KoujiName(models.Model):
    """新修繕計画データ"""

    version = models.ForeignKey(MasterPlan, verbose_name="Ver", on_delete=models.PROTECT)
    # simulation計算時に予定した工事を中止した場合にdo_calc=Falseとしてシミュレーションする。
    # 上記以外では使用しない。（本当はBooleaeFieldでよかったけれど）
    do_calc = models.IntegerField(verbose_name="計算対象", default=1)
    kouji_type = models.ForeignKey(MasterKoujiType, on_delete=models.PROTECT, verbose_name="工事種別")
    kouji_name = models.CharField(verbose_name="工事名", max_length=128)
    kouji_spec = models.CharField(verbose_name="工事仕様", max_length=128, blank=True)
    kouji_quantity = models.FloatField(verbose_name="施工数量")
    unit = models.ForeignKey(MasterUnit, verbose_name="単位", on_delete=models.PROTECT, null=True)
    unit_price = models.IntegerField(verbose_name="工事単価")
    kouji_year = models.IntegerField(verbose_name="施工予定年")
    comment = models.TextField(verbose_name="備考", blank=True, null=True)
    complete = models.BooleanField(verbose_name="工事完了", default=False)
    actual_cost = models.IntegerField(verbose_name="実工事費", default=0)

    def __str__(self):
        return self.kouji_name

    objects = KoujiNameQuerySet.as_manager()
