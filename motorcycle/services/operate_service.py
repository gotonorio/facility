import datetime

from django.db.models import Count
from facility.services import select_period

from motorcycle.models import MotorCycleSpace


def get_latest_motorcycle_date():
    """バイク置場データから使用中の最新日付を取得"""
    return (
        MotorCycleSpace.objects.filter(status_of_use="使用中")
        .values_list("date", flat=True)
        .order_by("-date")
        .first()
    )


def get_monthly_motorcycle_empty_list():
    """日付ごとの空き状況リストを取得（UI表示用）"""
    return (
        MotorCycleSpace.objects.values("date")
        .annotate(count=Count("date"))
        .filter(status_of_use="空き")
        .order_by("-date")
    )


def run_motorcycle_monthly_copy(year, month):
    """
    指定年月のデータを一括生成する。
    成功時は (True, message)、失敗時は (False, message) を返す。
    """
    new_date = datetime.date(int(year), int(month), 1)

    # 重複チェック
    if MotorCycleSpace.objects.filter(date=new_date).exists():
        return False, f"バイク置場の{new_date}は既に存在しています。"

    # 最新データの取得
    latest_date = get_latest_motorcycle_date()
    if not latest_date:
        return False, "コピー元となる最新データが見つかりません。"

    # 抽出期間の決定とコピー実行
    tstart, tend = select_period(latest_date.year, latest_date.month)
    old_records = MotorCycleSpace.objects.filter(date__range=[tstart, tend]).order_by("no")

    new_records = [
        MotorCycleSpace(
            no=d.no,
            room_no=d.room_no,
            date=new_date,
            status_of_use=d.status_of_use,
            comment=d.comment,
        )
        for d in old_records
    ]

    MotorCycleSpace.objects.bulk_create(new_records)
    return True, f"{new_date}のデータを{len(new_records)}件作成しました。"
