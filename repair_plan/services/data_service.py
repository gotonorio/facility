import logging

from django.db import transaction
from django.db.models.aggregates import Max

from repair_plan.models import (
    KoujiName,
    MasterPlan,
)

logger = logging.getLogger(__name__)


def get_max_master_version():
    """現在の最大バージョンを取得"""
    return MasterPlan.objects.aggregate(ver=Max("version"))["ver"]


def duplicate_repair_plan(*, source_plan: MasterPlan, new_version: int, author=None):
    """
    長期修繕計画を複製するサービス関数
    - 引数に*を置くことでキーワード引数のみを受け付けるようにする。
    :param source_plan: 複製元の MasterPlan インスタンス
    :param new_version: 新しいバージョン番号
    :param author: 操作者（任意）
    :return: 新しく作成した MasterPlan
    """

    # -----------------------------
    # 事前チェック
    # -----------------------------
    if MasterPlan.objects.filter(version=new_version).exists():
        raise ValueError(f"Ver.{new_version} は既に存在しています。")

    # -----------------------------
    # トランザクション開始
    # -----------------------------
    with transaction.atomic():
        # ① MasterPlan を複製
        new_plan = MasterPlan.objects.create(
            version=new_version,
            first_year=source_plan.first_year,
            final_year=source_plan.final_year,
            balance=source_plan.balance,
            only_manager=source_plan.only_manager,
            comment=f"Ver.{source_plan.version} を複製",
        )

        # ② KoujiName を複製
        kouji_qs = KoujiName.objects.filter(version=source_plan)

        kouji_instances = []
        for kouji in kouji_qs:
            kouji.pk = None  # ★ 重要：新規作成
            kouji.version = new_plan
            kouji_instances.append(kouji)

        KoujiName.objects.bulk_create(kouji_instances)

        # -----------------------------
        # ログ
        # -----------------------------
        logger.info(
            f"RepairPlan duplicated: from Ver.{source_plan.version} to Ver.{new_version}, by {author}"
        )

    return new_plan


# def bulk_delete_kouji_by_version(version_name):
#     """指定バージョンの工事データを一括削除"""
#     # deleted_count, _ = KoujiName.objects.filter(version=version_obj).delete()
#     msg = KoujiName.objects.delete_koujiname_by_ver(version_name)
#     return msg
