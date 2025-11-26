from django.db import models


STATUS_OF_USE = (
    ("空き", "空き"),
    ("使用中", "使用中"),
)


class MotorCycleSpace(models.Model):
    """オートバイ駐車場"""

    no = models.IntegerField(verbose_name="駐車場No", default=0)
    room_no = models.IntegerField(verbose_name="部屋番号", default=0)
    date = models.DateField("年月", blank=True, null=True)
    status_of_use = models.CharField(
        verbose_name="使用状況", choices=STATUS_OF_USE, max_length=6, default="空き"
    )
    comment = models.CharField(verbose_name="備考", max_length=128, blank=True, null=True)

    def __str__(self):
        return self.status_of_use
