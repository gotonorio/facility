import logging

from django.db import models
from django.db.models import Count, Q, Sum
from django.utils import timezone
from facility.services import select_period

logger = logging.getLogger(__name__)


class ParkingType(models.Model):
    """駐車場のタイプ"""

    parking_type = models.CharField("駐車場タイプ", max_length=64)
    rent_fee = models.IntegerField("月額使用料")

    def __str__(self):
        return self.parking_type


STATUS = (
    ("使用中", "使用中"),
    ("空き", "空き"),
    ("一時利用", "一時利用"),
    ("予約中", "予約中"),
    ("解約予定", "解約予定"),
    ("使用中止", "使用中止"),
)


class ParkingSpaceQuerySet(models.QuerySet):
    """駐車場スペースのQuerySet
    - querysetを返すメソッドを定義（フィルタリングや集計など）
    - Managerクラスが呼び出す
    """

    def get_parking_space(self, year, month, parking_type):
        """タイプ別の駐車場情報を抽出するquerysetを返す"""
        # 抽出期間 余計なことはしない。月次処理を忘れたら、表示しない。
        tstart, tend = select_period(year, month)
        qs = self.select_related("parking_type").filter(payment_date__range=[tstart, tend])
        if parking_type:
            qs = qs.filter(parking_type=parking_type)
        return qs

    def get_parking_space_num(self, year, month, parking_type):
        """利用可能駐車場スペースの数を返す"""
        # 使用中止の駐車場番号
        exclude_no = (44, 46, 48, 50, 52, 54, 56, 58, 60, 62, 64)
        tstart, tend = select_period(year, month)
        qs = self.exclude(no__in=exclude_no).filter(payment_date__range=[tstart, tend])

        if parking_type:
            qs = qs.filter(parking_type=parking_type)
        return qs.count()

    def get_parking_rireki(self, year):
        """指定された年の収入履歴を返す
        https://stackoverflow.com/questions/33775011/how-to-annotate-count-with-a-condition-in-a-django-queryset
        https://docs.djangoproject.com/ja/3.0/ref/models/conditional-expressions/
        """
        qs = (
            self.get_parking_space(year, "ALL", "")
            .values("payment_date")
            .annotate(
                uses=Count(
                    "id",
                    filter=(Q(status_of_use="使用中") | Q(status_of_use="解約予定")),
                    distinct=True,
                ),
                nouses=Count(
                    "id",
                    filter=(Q(status_of_use="空き") | Q(status_of_use="予約中")),
                    distinct=True,
                ),
                income=Sum(
                    "parking_type__rent_fee",
                    filter=(Q(status_of_use="使用中") | Q(status_of_use="解約予定")),
                ),
                noincome=Sum(
                    "parking_type__rent_fee",
                    filter=(
                        Q(status_of_use="空き") | Q(status_of_use="使用中止") | Q(status_of_use="予約中")
                    ),
                ),
            )
        )
        return qs

    def get_empty_space(self, year, month, parking_type):
        return ParkingSpace.get_empty_space(year, month, parking_type)


class ParkingSpaceManager(models.Manager):
    """駐車場スペースのManager"""

    # カスタムQuerySet（ParkingSpaceQuerySet）を指定
    def get_queryset(self):
        return ParkingSpaceQuerySet(self.model, using=self._db)

    def get_parking_space(self, year, month, parking_type):
        return self.get_queryset().get_parking_space(year, month, parking_type)

    def get_parking_space_num(self, year, month, parking_type):
        return self.get_queryset().get_parking_space_num(year, month, parking_type)

    def get_parking_rireki(self, year):
        """指定された年の収入履歴を返す"""
        return self.get_queryset().get_parking_rireki(year)

    def get_empty_space(self, year, month, parking_type):
        """空き駐車場のquerysetとその数を返す
        querysetだけ返すならばQuerySetのメソッドにするべきだが、数も返すためManagerのメソッドとする
        """
        tstart, tend = select_period(year, month)
        qs = self.select_related("parking_type").filter(payment_date__range=[tstart, tend])
        qs = qs.filter(Q(status_of_use="空き") | Q(status_of_use="予約中"))
        if parking_type:
            qs = qs.filter(parking_type=parking_type)
        return qs, qs.count()


class ParkingSpace(models.Model):
    """駐車スペースモデル"""

    no = models.IntegerField(verbose_name="駐車No", default=0)
    parking_type = models.ForeignKey(ParkingType, on_delete=models.PROTECT, verbose_name="駐車場タイプ")
    name = models.CharField(verbose_name="契約者", max_length=16, blank=True, null=True)
    room_number = models.IntegerField(verbose_name="部屋番号", default=0)
    payment_date = models.DateField(verbose_name="年月", blank=True, null=True)
    status_of_use = models.CharField(verbose_name="利用状況", choices=STATUS, max_length=32, default="使用中")
    comment = models.TextField(verbose_name="備考", blank=True)
    created_date = models.DateTimeField(verbose_name="作成日", default=timezone.now)

    class Meta:
        unique_together = ("no", "payment_date")

    def __str__(self):
        return self.status_of_use

    objects = ParkingSpaceManager()
