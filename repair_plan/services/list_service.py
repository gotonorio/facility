from django.db.models import F, IntegerField, Sum
from facility.services import get_latest_version

from repair_plan.models import KoujiName


def get_version_and_manager_info(user, requested_version=None):
    """ユーザー権限と適切なバージョン番号を取得する"""
    latest_version, is_manager = get_latest_version(user)
    version = requested_version or latest_version
    return version, is_manager


def calculate_repair_total(queryset):
    """クエリセットから合計金額（単価×数量）を計算する"""
    total = sum(item.unit_price * item.kouji_quantity for item in queryset)
    return int(total)


def get_repair_plan_summary(version, kouji_type="ALL"):
    """長期修繕計画の一覧と合計を取得"""
    queryset = KoujiName.objects.get_koujiname_list(version, kouji_type).order_by("kouji_year", "kouji_type")
    return queryset, calculate_repair_total(queryset)


def get_yearly_repair_summary(version, year):
    """特定年度の修繕計画と合計を取得"""
    queryset = KoujiName.objects.get_repair_plan_list_by_year(version, year).order_by(
        "kouji_type", "kouji_name"
    )
    return queryset, calculate_repair_total(queryset)


def get_koujitype_aggregation(version):
    """工事種別ごとの集計（annotateを使用）"""
    qs = (
        KoujiName.objects.get_koujiname_list(version, "ALL")
        .values("kouji_type__master_name")
        .annotate(subtotal=Sum(F("kouji_quantity") * F("unit_price"), output_field=IntegerField()))
        .order_by("kouji_type")
    )
    total = qs.aggregate(total=Sum("subtotal"))["total"] or 0
    return qs, int(total)
