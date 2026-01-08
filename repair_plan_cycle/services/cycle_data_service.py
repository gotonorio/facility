from repair_plan_cycle.models import KoujiCycleData


def get_cycledata_version():
    """工事周期データのバージョンをリストで返す"""
    qs = KoujiCycleData.objects.all()
