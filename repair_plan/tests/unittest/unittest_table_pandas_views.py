from django.test import TestCase

from .test_permissions import PermissionRequiredViewTestMixin


class RepairPlanPandasViewTests(PermissionRequiredViewTestMixin, TestCase):
    """table_pandas_views.pyのテスト"""

    # RepairPlanPandasView呼び出しurl
    url_name = "repair_plan:repairplan_pandas"
    # アプリケーション名
    permission_app_label = "repair_plan"
    # 必要パーミッション
    permission_codename = "add_koujiname"
