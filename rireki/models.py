from django.db import models
from repair_plan.models import MasterKoujiType


class AccountType(models.Model):
    """支出区分"""

    name = models.CharField(max_length=32)

    def __str__(self):
        return self.name


class KoujiRireki(models.Model):
    """工事履歴"""

    year = models.IntegerField(default=2009)
    month = models.IntegerField(null=True, blank=True)
    koujitype = models.ForeignKey(MasterKoujiType, on_delete=models.PROTECT, null=True, blank=True)
    koujimei = models.CharField(max_length=256)
    cost = models.BigIntegerField(null=True, blank=True)
    constractor = models.CharField(max_length=64, null=True, blank=True)
    account_type = models.ForeignKey(AccountType, on_delete=models.PROTECT, null=True, blank=True)
    comment = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.koujimei

    # costの合計をpython関数で求める。
    def calc_total(self, sql):
        cost_list = sql
        total = 0
        for data in cost_list:
            total += data.cost
        return total
