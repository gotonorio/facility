import calendar
import logging

from django.db.models import Max
from django.utils import timezone
from register.models import User
from repair_plan.models import MasterPlan

logger = logging.getLogger(__name__)


def select_period(year, month):
    """検索期間を返す"""
    if str(month).upper() == "ALL":
        tstart = timezone.datetime(int(year), 1, 1, 0, 0, 0)
        tend = timezone.datetime(int(year), 12, 31, 0, 0, 0)
    else:
        last_day = calendar.monthrange(int(year), int(month))[1]
        tstart = timezone.datetime(int(year), int(month), 1, 0, 0, 0)
        tend = timezone.datetime(int(year), int(month), last_day, 0, 0, 0)
    return tstart, tend


def get_latest_version(user_name):
    """グループ権限に応じた最新の計画マスタバージョン番号を返す"""
    # forms.pyのversionセレクタに引数と初期値を設定する。引数の「True」は__init__()で受け取ることができる。
    group_name = User.group_name(user_name)
    is_manager = False
    # if group_name in ["chairman", "repair_plan_manager", "specialist_committee"]:
    if group_name in ["chairman", "repair_plan_manager"]:
        latest_ver = MasterPlan.objects.aggregate(ver=Max("version"))
        is_manager = True
    else:
        latest_ver = MasterPlan.objects.filter(only_manager=False).aggregate(ver=Max("version"))

    return latest_ver["ver"], is_manager
