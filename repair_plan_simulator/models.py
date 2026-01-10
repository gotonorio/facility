from decimal import Decimal

from django.db import models
from django.db.models import Max


class Shuuzenhi_income(models.Model):
    """修繕計画初年度からの実修繕積立金
    - 毎年の修繕積立金を登録して、それをシミュレーションに使用する。
    - 駐車場会計を分離独立したためparking_kanrihiは不要。
    """

    year = models.IntegerField()
    income = models.IntegerField(default=0)
    parking_income = models.IntegerField(default=0)
    parking_kanrihi = models.IntegerField(default=0)
    extra_income = models.IntegerField(default=0)
    real = models.BooleanField(default=False)
    comment = models.TextField(verbose_name="備考", blank=True, null=True)

    def __int__(self):
        return self.income + self.parking_income + self.extra_income - self.parking_kanrihi


class ConsumerPriceIndex(models.Model):
    """物価指数モデル
    - シミュレーション計算時にだけ利用するモデル。
    """

    year = models.IntegerField(verbose_name="西暦", unique=True)
    cpi = models.DecimalField(verbose_name="物価指数", max_digits=4, decimal_places=3, default=1.000)
    comment = models.TextField(verbose_name="備考", blank=True, null=True)

    def __int__(self):
        return self.cpi

    # 修繕計画の開始、終了年を返す。
    @classmethod
    def get_lastyear(cls):
        last_year = cls.objects.aggregate(last_year=Max("year"))
        return last_year

    # cpiを保存する
    @classmethod
    def save_continuas_cpi(cls, start_year, last_year, year_cpi, comment):
        """指定期間の物価上昇率を保存"""
        error_list = []
        index_cpi = year_cpi - Decimal("1.0")
        first = True

        for this_year in range(start_year, last_year + 1):
            if first:
                this_cpi = year_cpi
                first = False
            else:
                this_cpi += index_cpi
                comment = ""
            # 保存処理（上書き保存する）
            try:
                cls.objects.update_or_create(
                    year=this_year,
                    defaults={"year": this_year, "cpi": this_cpi, "comment": comment},
                )
            except Exception as e:
                error_list.append(f"西暦{this_year}で「{e}」のエラーが発生")
        return error_list
