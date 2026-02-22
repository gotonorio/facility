from django.conf import settings
from django.db.models import Max, Q
from django.utils import timezone
from django.utils.timezone import localtime

from parking.models import ParkingSpace, ParkingType


def get_parking_summary(year, month, parking_type_id=None):
    """指定年月の駐車場リストと使用料合計を取得"""
    qs = ParkingSpace.objects.get_parking_space(year, month, parking_type_id).order_by("no")

    # 合計金額の計算
    total = sum(d.parking_type.rent_fee for d in qs if d.status_of_use in ["使用中", "解約予定"])
    return qs, total


def categorize_parking_spaces(qs):
    """駐車場番号に基づいて3つのセクションに分割（UI表示用）"""
    space1, space2, space3 = [], [], []
    for space in qs:
        data = [space.no, space.parking_type, space.status_of_use, space.parking_type.rent_fee]
        if space.no < 43:
            space1.append(data)
        elif space.no < 87:
            space2.append(data)
        else:
            space3.append(data)
    return space1, space2, space3


def get_parking_diagram_data(year, month):
    """
    図解表示用のデータを取得。データがない場合は最新の月へフォールバックする。
    Returns: (queryset, actual_year, actual_month)
    """
    qs = ParkingSpace.objects.get_parking_space(year, month, "").order_by("no")

    if not qs.exists():
        latest_date = ParkingSpace.objects.aggregate(Max("payment_date"))["payment_date__max"]
        if latest_date:
            year, month = latest_date.year, latest_date.month
            qs = ParkingSpace.objects.get_parking_space(year, month, "").order_by("no")

    return qs, year, month


def get_utilization_metrics(year, month):
    """各駐車場タイプの稼働率を計算"""
    metrics = {
        "plain": {"name": settings.PLAIN_PARKING, "total": 0, "empty": 0, "used": 0, "rate": 0},
        "machine_up": {"name": settings.MACHINE_UP_PARKING, "total": 0, "empty": 0, "used": 0, "rate": 0},
        "machine_down": {"name": settings.MACHINE_DOWN_PARKING, "total": 0, "empty": 0, "used": 0, "rate": 0},
        "overall_rate": 0,
    }

    # 各タイプごとの集計関数
    def fill_metric(key, type_name):
        try:
            ptype = ParkingType.objects.get(parking_type=type_name)
            total = ParkingSpace.objects.get_parking_space_num(year, month, ptype)
            if total > 0:
                _, empty = ParkingSpace.objects.get_empty_space(year, month, ptype)
                metrics[key]["total"] = total
                metrics[key]["empty"] = empty
                metrics[key]["used"] = total - empty
                metrics[key]["rate"] = int((total - empty) * 100 / total)
                return True
        except ParkingType.DoesNotExist:
            pass
        return False

    has_data = fill_metric("plain", settings.PLAIN_PARKING)
    fill_metric("machine_up", settings.MACHINE_UP_PARKING)
    fill_metric("machine_down", settings.MACHINE_DOWN_PARKING)

    if has_data:
        total_all = (
            metrics["plain"]["total"] + metrics["machine_up"]["total"] + metrics["machine_down"]["total"]
        )
        used_all = metrics["plain"]["used"] + metrics["machine_up"]["used"] + metrics["machine_down"]["used"]
        if total_all > 0:
            metrics["overall_rate"] = int(used_all * 100 / total_all)

    return metrics, has_data


def get_income_history_metrics(year):
    """駐車場収入履歴の取得と合計計算"""
    qs = ParkingSpace.objects.get_parking_rireki(year).order_by("-payment_date")

    total = 0
    noincome = 0
    for d in qs:
        total += d["income"]
        noincome += d["noincome"]

    return qs, total, noincome


def get_parking_fee_csv_data(year):
    """CSV出力用のクエリセットを取得"""
    return (
        ParkingSpace.objects.filter(Q(status_of_use="使用中") | Q(status_of_use="解約予定"))
        .filter(payment_date=year)
        .order_by("room_number")
    )


# Formデータ、url変数の取得
def resolve_year_month(url_year, url_month, get_year, get_month):
    local_now = localtime(timezone.now())

    year = url_year or get_year or local_now.year
    month = url_month or get_month or local_now.month

    return int(year), int(month)
