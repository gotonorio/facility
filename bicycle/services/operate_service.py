import datetime

from dateutil.relativedelta import relativedelta
from django.db.models import Count
from facility.services import select_period

from bicycle.models import BicycleSpace


def get_latest_bicycle_date():
    """駐輪場データから使用中の最新日付を取得"""
    latest = (
        BicycleSpace.objects.filter(status_of_use="使用中")
        .values_list("date", flat=True)
        .order_by("-date")
        .first()
    )
    return latest


def get_monthly_bicycle_empty_counts():
    """登録済みデータの日付別空き数を取得（UI表示用）"""
    return (
        BicycleSpace.objects.values("date")
        .annotate(count=Count("date"))
        .filter(status_of_use="空き")
        .order_by("-date")
    )


def run_bicycle_monthly_processing(year, month):
    """
    指定年月の駐輪場データを一括生成する。
    Returns: (bool, message)
    """
    new_date = datetime.date(int(year), int(month), 1)

    # 重複チェック
    if BicycleSpace.objects.filter(date=new_date).exists():
        return False, f"駐輪場の{new_date}は既に存在しています。"

    # コピー元となる最新日付の取得
    latest_date = get_latest_bicycle_date()
    if not latest_date:
        return False, "元となるデータが見つかりません。"

    # 期間選択（既存の外部サービスを利用）
    tstart, tend = select_period(latest_date.year, latest_date.month)
    old_qs = BicycleSpace.objects.filter(date__range=[tstart, tend]).order_by("no")

    new_records = [
        BicycleSpace(
            no=d.no,
            location=d.location,
            room_number=d.room_number,
            date=new_date,
            status_of_use=d.status_of_use,
            comment=d.comment,
        )
        for d in old_qs
    ]

    BicycleSpace.objects.bulk_create(new_records)
    return True, f"{new_date}の駐輪場データを{len(new_records)}件作成しました。"
