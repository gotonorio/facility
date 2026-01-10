from django.db.models import Max

from repair_plan_cycle.models import KoujiCycleData


def get_cycledata_latest_version(requested_version=None):
    """最新の周期データのバージョン番号を返す"""
    # forms.pyのversionセレクタに引数と初期値を設定する。引数の「True」は__init__()で受け取ることができる。
    latest_version = KoujiCycleData.objects.aggregate(ver=Max("version"))
    version = requested_version or latest_version["ver"]

    return version


def get_cycledata(version):
    """指定されたversionの周期データの一覧を取得"""
    queryset = KoujiCycleData.objects.filter(version=version).order_by("kouji_type")
    return queryset
