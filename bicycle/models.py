import logging

from django.conf import settings
from django.db import models
from django.db.models import Count, Q
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


class BicycleSpaceQuerySet(models.QuerySet):
    """駐輪場スペースのQuerySet
    - querysetを返すメソッドを定義（フィルタリングや集計など）
    - Managerクラスが呼び出す
    """

    def get_bicycle_space(self, year, month, location):
        """タイプ別の駐輪場情報を抽出するquerysetを返す
        - クラセルでは全データをコピーするため、ここでも全データ（空き、契約・解約予定）を抽出すること。
        """
        # 抽出期間
        tstart, tend = select_period(year, month)
        if location:
            qs = self.filter(date__range=[tstart, tend], location=location)
        else:
            qs = self.filter(date__range=[tstart, tend])
        return qs

    def get_bicycle_incomehistory(self, year):
        """指定された年の収入履歴を返す
        https://stackoverflow.com/questions/33775011/how-to-annotate-count-with-a-condition-in-a-django-queryset
        https://docs.djangoproject.com/ja/3.0/ref/models/conditional-expressions/
        """
        qs = (
            self.get_bicycle_space(year, "ALL", "")
            .values("date")
            .annotate(
                uses=Count(
                    "id",
                    filter=(Q(status_of_use="使用中") | Q(status_of_use="解約予定")),
                    distinct=True,
                ),
                income=settings.BICYCLE_USAGE_FEE
                * Count(
                    "id",
                    filter=(Q(status_of_use="使用中") | Q(status_of_use="解約予定")),
                ),
            )
        )
        return qs


class BicycleSpaceManager(models.Manager):
    """駐輪場スペースのManager"""

    # カスタムQuerySet（ParkingSpaceQuerySet）を指定
    def get_queryset(self):
        return BicycleSpaceQuerySet(self.model, using=self._db)

    def get_bicycle_space(self, year, month, location):
        return self.get_queryset().get_bicycle_space(year, month, location)

    def get_bicycle_incomehistory(self, year):
        """指定された年の収入履歴を返す"""
        return self.get_queryset().get_bicycle_incomehistory(year)


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

    objects = BicycleSpaceManager()
