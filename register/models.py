import logging

from django.contrib.auth.models import AbstractUser, BaseUserManager, Group
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.dispatch import receiver
from django.utils import timezone

logger = logging.getLogger(__name__)


class UserManager(BaseUserManager):
    """User の論理削除対応 Manager"""

    def get_queryset(self):
        # is_deleted=False のみをデフォルトで返す
        return super().get_queryset().filter(is_deleted=False)

    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError("Username is required")
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(username, password, **extra_fields)


class AllUserManager(BaseUserManager):
    """論理削除ユーザーも全て返す Manager"""

    def get_queryset(self):
        return super().get_queryset()


class User(AbstractUser):
    """論理削除対応のUserモデル
    - is_deletedフラグを追加
    - deleted_atフィールドを追加
    """

    # Manager を上書き
    objects = UserManager()
    all_objects = AllUserManager()  # 削除済も含む

    is_deleted = models.BooleanField(default=False, verbose_name="削除フラグ")
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name="削除日時")

    class Meta:
        verbose_name = "ユーザー"
        verbose_name_plural = "ユーザー"

    # 論理削除
    def delete(self, using=None, keep_parents=False):
        """物理削除の代わりに削除フラグを立てる"""
        self.is_active = False  # ログイン不可にする
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=["is_active", "is_deleted", "deleted_at"])

    def hard_delete(self, using=None, keep_parents=False):
        """完全に物理削除する場合はこちらを明示的に呼ぶ"""
        super().delete(using=using, keep_parents=keep_parents)

    def group_name(user_name):
        """ユーザの所属するグループ名をリストで返す"""
        user_groups = user_name.groups.all()
        # ユーザーが所属するグループの名前を取得する
        group_names = [group.name for group in user_groups]
        return group_names[0]


@receiver(models.signals.post_save, sender=User)
def post_save_user_signal_handler(sender, instance, created, **kwargs):
    """シグナルによってUserにデフォルトgroupを追加する。
    https://stackoverflow.com/questions/51974276/how-to-automatically-add-group-and-staff-permissions-when-user-is-created/51975193
    """
    if created:
        try:
            group = Group.objects.get(name="guest")
            instance.groups.add(group)
        except ObjectDoesNotExist:
            pass


@receiver(user_logged_in)
def user_logged_in_callback(sender, request, user, **kwargs):
    """ログインした際に呼ばれて、管理者ならログ記録する"""
    if user_is_manager(request, user):
        logger.info(f"{user} login")


@receiver(user_logged_out)
def user_logged_out_callback(sender, request, user, **kwargs):
    """ログアウトした際に呼ばれる"""
    if user_is_manager(request, user):
        logger.info(f"{user} logout")


def user_is_manager(request, user):
    """userが「管理者」どうかの判定(adminuserは除外)"""
    return user.groups.filter(name__in=["chairman", "master"]).exists()
