import logging

from django.db import models
from facility.services import select_period

logger = logging.getLogger(__name__)

LOCATION = (
    ("棟前", "棟前"),
    ("棟東", "棟東"),
    ("棟北", "棟北"),
    ("平置き", "平置き"),
)

STATUS_OF_USE = (
    ("空き", "空き"),
    ("使用中", "使用中"),
    ("契約予定", "契約予定"),
    ("解約予定", "解約予定"),
)


class BicycleSpace(models.Model):
    """駐輪場スペースモデル"""

    no = models.IntegerField(verbose_name="駐輪場No", default=0)
    location = models.CharField(verbose_name="駐輪場所", choices=LOCATION, max_length=4, default="棟前")
    room_number = models.IntegerField(verbose_name="部屋番号", default=0)
    date = models.DateField("年月", blank=True, null=True)
    status_of_use = models.CharField(
        verbose_name="使用状況", choices=STATUS_OF_USE, max_length=6, default="空き"
    )
    comment = models.TextField(verbose_name="備考", blank=True)

    def __str__(self):
        return self.status_of_use

    @classmethod
    def get_bicycle_space(cls, year, month, location):
        """タイプ別の駐輪場情報を抽出するquerysetを返す
        - クラセルでは全データをコピーするため、ここでも全データ（空き、契約・解約予定）を抽出すること。
        """
        # 抽出期間
        tstart, tend = select_period(year, month)
        qs = cls.objects
        if location:
            qs = qs.filter(date__range=[tstart, tend], location=location)
        else:
            qs = qs.filter(date__range=[tstart, tend])
        return qs
