from django.test import TestCase

from .test_permissions import LoginRequiredViewTestMixin


class RepairPlanListViewTests(LoginRequiredViewTestMixin, TestCase):
    """list_views.pyのテスト"""

    # RepairPlanPandasView呼び出しurl
    url_name = "repair_plan:repairplan_list"
    # アプリケーション名
    permission_app_label = "repair_plan"
