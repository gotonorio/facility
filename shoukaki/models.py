from django.db import models


class ShoukakiType(models.Model):
    """消火器種類"""

    name = models.CharField("品番", max_length=64)
    shoukaki_type = models.CharField("種類", max_length=128)
    keisiki = models.CharField("形式番号", max_length=128)
    maker = models.CharField("製造会社", max_length=128, blank=True, null=True)
    valid_period = models.IntegerField("有効期間", default=10)
    price = models.IntegerField("購入価格", blank=True, null=True)
    alive = models.BooleanField("有効", default=True)

    def __str__(self):
        return self.name


class Shoukaki(models.Model):
    """消火器モデル"""

    code = models.IntegerField("No", default=0)
    shoukaki = models.ForeignKey(ShoukakiType, on_delete=models.PROTECT)
    location = models.CharField("設置場所", max_length=32)
    installation_date = models.DateField("設置日", blank=True, null=True)
    inspection_date = models.DateField("点検日", blank=True, null=True)
    made_year = models.IntegerField("製造年", default=1999)
    made_no = models.CharField("製造番号", max_length=64, unique=True)
    comment = models.TextField("備考", blank=True)
    alive = models.BooleanField("有効", default=True)

    def __str__(self):
        return self.location
