import datetime

from django.db.models import Count, Q

from parking.models import ParkingSpace


def get_monthly_empty_counts():
    """月毎の空き・予約中駐車場数を取得"""
    return (
        ParkingSpace.objects.values("payment_date")
        .annotate(count=Count("payment_date"))
        .filter(Q(status_of_use="空き") | Q(status_of_use="予約中"))
        .order_by("-payment_date")
    )


def get_latest_active_date():
    """使用中・解約予定の最新日付を取得"""
    latest = (
        ParkingSpace.objects.filter(Q(status_of_use="使用中") | Q(status_of_use="解約予定"))
        .values_list("payment_date", flat=True)
        .order_by("-payment_date")
        .first()
    )
    return latest


def run_monthly_batch_copy(year, month):
    """
    指定年月のデータを、最新月のデータを元に一括作成する。
    成功した場合はTrue、既に存在する場合はFalseを返す。
    """
    new_date = datetime.date(int(year), int(month), 1)

    # 重複チェック
    if ParkingSpace.objects.filter(payment_date=new_date).exists():
        return False, f"{new_date}のデータは既に存在します。"

    # 元となる最新データの取得
    latest_date = get_latest_active_date()
    if not latest_date:
        return False, "元となるデータが見つかりません。"

    old_records = ParkingSpace.objects.filter(payment_date=latest_date)
    new_records = [
        ParkingSpace(
            no=d.no,
            parking_type=d.parking_type,
            name=d.name,
            room_number=d.room_number,
            payment_date=new_date,
            comment=d.comment,
            status_of_use=d.status_of_use,
        )
        for d in old_records
    ]

    ParkingSpace.objects.bulk_create(new_records)
    return True, f"{new_date}のデータを{len(new_records)}件作成しました。"
