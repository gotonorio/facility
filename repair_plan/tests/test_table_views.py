from django.test import TestCase

from .test_permissions import PermissionRequiredViewTestMixin


class RepairPlanPandasViewTests(PermissionRequiredViewTestMixin, TestCase):
    """長期修繕計画表（管理者用）のテスト"""

    # RepairPlanPandasView呼び出しurl
    url_name = "repair_plan:repairplan_table"
    # アプリケーション名
    permission_app_label = "repair_plan"
    # 必要パーミッション
    permission_codename = "add_koujiname"
