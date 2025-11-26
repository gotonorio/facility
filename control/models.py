from django.db import models
from django.utils import timezone


class ControlRecord(models.Model):
    """プロジェクトのコントロール用定数を定義"""

    # 仮登録メニューの表示/非表示コントロール
    tmp_user_flg = models.BooleanField(verbose_name="仮登録", default=False)
    # add your control variable

    @classmethod
    def show_tmp_user_menu(cls):
        return cls.objects.get("tmp_user_flg")


class Description(models.Model):
    """説明画面用モデル
    - データ入力の説明文を保持するためだけのモデル。
    - 新規作成は無し。UpdateViewのみ。
    """

    title = models.CharField(verbose_name="タイトル", max_length=32)
    description = models.TextField(verbose_name="説明文")
    alive = models.BooleanField(verbose_name="有効", default=True)
    created_date = models.DateTimeField(verbose_name="作成日", default=timezone.now)
    only_manager = models.BooleanField(verbose_name="管理者専用", default=False)

    def __str__(self):
        return self.title
