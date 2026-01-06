import logging

from django.conf import settings
from django.db.models import Count

from bicycle.models import BicycleSpace

logger = logging.getLogger(__name__)


def get_bicycle_summary(year, month):
    """駐輪場の配置別リストと合計金額を取得"""
    qs = BicycleSpace.objects.get_bicycle_space(year, month, "").order_by("no")

    # 配置別仕分け
    categorized = {"space1": [], "space2": [], "space3": [], "space4": []}

    count_use = 0
    for space in qs:
        # 使用中・解約予定のカウント
        if space.status_of_use in ["使用中", "解約予定"]:
            count_use += 1

        data = [space.no, space.location, space.status_of_use, space.pk, space.room_number]

        if space.location == "平置き":
            categorized["space1"].append(data)
        elif space.location == "棟前":
            categorized["space2"].append(data)
        elif space.location == "棟東":
            categorized["space3"].append(data)
        elif space.location == "棟北":
            categorized["space4"].append(data)
        else:
            logger.debug(f"{space.no}の配置データが不明です。")

    total_fee = count_use * settings.BICYCLE_USAGE_FEE
    return categorized, total_fee, qs


def get_bicycle_by_room(year, month):
    """住戸別の駐輪場リストを取得"""
    qs = (
        BicycleSpace.objects.get_bicycle_space(year, month, "")
        .exclude(room_number=0)
        .order_by("room_number", "no")
    )
    count_use = qs.filter(status_of_use="使用中").count()
    return qs, count_use * settings.BICYCLE_USAGE_FEE


def get_bicycle_fee_by_room(year, month):
    """住戸別の駐輪場使用料集計を取得（管理者用）"""
    qs = (
        BicycleSpace.objects.get_bicycle_space(year, month, "")
        .exclude(room_number=0)
        .values("room_number")
        .annotate(num=Count("no"), fee=Count("no") * settings.BICYCLE_USAGE_FEE)
        .order_by("room_number")
    )

    # 合計金額の計算
    total = sum(item["fee"] for item in qs)
    return qs, total


def get_bicycle_income_summary(year):
    """駐輪場収入履歴の取得と合計計算"""
    qs = BicycleSpace.objects.get_bicycle_incomehistory(year).order_by("-date")
    total = sum(d["income"] for d in qs)
    return qs, total
