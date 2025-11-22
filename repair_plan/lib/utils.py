from django.db.models.aggregates import Max

from register.models import User
from repair_plan.models import MasterPlan


def get_latest_version(user_name):
    """グループ権限に応じた最新の計画バージョン番号を返す"""
    # forms.pyのversionセレクタに引数と初期値を設定する。引数の「True」は__init__()で受け取ることができる。
    group_name = User.group_name(user_name)
    is_manager = False
    if group_name in ["chairman", "repair_plan_manager", "specialist_committee"]:
        latest_ver = MasterPlan.objects.aggregate(ver=Max("version"))
        is_manager = True
    else:
        latest_ver = MasterPlan.objects.filter(only_manager=False).aggregate(
            ver=Max("version")
        )

    return latest_ver["ver"], is_manager
