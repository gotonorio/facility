from django.urls import path

from repair_plan_simulator import views

app_name = "repair_plan_simulator"
urlpatterns = [
    # データ表示
    path("do_simulate/", views.SimulateView.as_view(), name="do_simulate"),
    path("simulate_data/", views.SimulateDataView.as_view(), name="simulate_data"),
    path("except_list/", views.SimulatePlanListView.as_view(), name="except_list"),
    # データの登録
    path("create_income/", views.CreateIncomeView.as_view(), name="create_income"),
    path("create_cpi/", views.CreateCPIView.as_view(), name="create_cpi"),
    # データの修正
    path("update_income/<int:pk>", views.UpdateIncomeView.as_view(), name="update_income"),
    path("reset_do_cal/<int:pk>", views.reset_do_calc, name="reset_do_calc"),
    path("unset_do_cal/<int:pk>", views.unset_do_calc, name="unset_do_calc"),
    path("update_cpi/<int:pk>", views.UpdateCPIView.as_view(), name="update_cpi"),
]
