# repair_plan_simulator/views/except_views.py
# -----------------------------------------------------------------------------
# 除外工事 do_calc ON/OFF
# -----------------------------------------------------------------------------

from django.shortcuts import get_object_or_404, redirect
from repair_plan.models import KoujiName
from repair_plan.views.data_views import RepairPlanUpdateListView


class SimulatePlanListView(RepairPlanUpdateListView):
    """除外工事の一覧"""

    template_name = "repair_plan_simulator/except_list.html"


def reset_do_calc(request, pk):
    instance = get_object_or_404(KoujiName, pk=pk)
    instance.do_calc = 1
    instance.save()
    return redirect("simulate:do_simulate")


def unset_do_calc(request, pk):
    instance = get_object_or_404(KoujiName, pk=pk)
    instance.do_calc = 0
    instance.save()
    return redirect("simulate:do_simulate")
