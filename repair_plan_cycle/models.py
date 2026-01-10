from django.db import models
from repair_plan.models import MasterKoujiType


class KoujiCycleData(models.Model):
    """長期修繕計画用の「工事周期データ」"""

    version = models.IntegerField(verbose_name="バージョン番号", default=0)
    kouji_type = models.ForeignKey(MasterKoujiType, on_delete=models.PROTECT, verbose_name="工事種別")
    kouji_name = models.CharField(verbose_name="工事名", max_length=128)
    first_year = models.IntegerField(verbose_name="初回工事年", default=0)
    repeat_cycle = models.IntegerField(verbose_name="工事周期", default=0)
    cost = models.IntegerField(verbose_name="工事費", default=0)
    comment = models.TextField(verbose_name="備考", blank=True, null=True)

    def __str__(self):
        return self.kouji_name

    @classmethod
    def delete_koujicycledata_by_ver(cls, ver: int) -> int:
        """指定されたバージョンのkoujicycleデータを削除し、削除件数を返す"""

        # 意図しない入力が来ないよう、引数の型をアノテーションで明確にする
        try:
            ver_int = int(ver)
        except ValueError:
            # ログ出力など適切なエラー処理を行うべき
            raise ValueError("バージョンは整数値として指定してください。")

        qs = cls.objects.filter(version=ver_int)

        # qs.delete() は (削除件数, {モデル名: 件数}) のタプルを返す
        deleted_count, _ = qs.delete()

        # 件数が0件の場合のメッセージは呼び出し側で処理するのが一般的だが、
        # シンプルに処理件数を返す

        return deleted_count
