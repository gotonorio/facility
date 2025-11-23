from django.urls import path

from repair_plan_cycle.views import cycledata_views, views

app_name = "repair_plan_cycle"
urlpatterns = [
    # 工事周期データの表示
    path("cycledata_list/", views.KoujiCycleDataListView.as_view(), name="cycledata_list"),
    # 工事周期データの新規作成
    path(
        "create_cycledata/",
        cycledata_views.CycleDataCreateView.as_view(),
        name="create_cycledata",
    ),
    # 工事周期データの修正
    path(
        "update_basicplandata/<int:pk>/",
        cycledata_views.CycleDataUpdateView.as_view(),
        name="update_basicplandata",
    ),
    # 工事周期データからの長期修繕計画けータ作成
    path("create_repairplan/", cycledata_views.RepairplanCreateView.as_view(), name="create_repairplan"),
    # 工事周期データの複製
    path(
        "duplicate_koujicycledata/",
        cycledata_views.DuplicateKoujiCycleDataView.as_view(),
        name="duplicate_koujicycledata",
    ),
    # 工事周期データの削除
    path(
        "delete_koujicycledata/",
        cycledata_views.DeleteKoujiCycleDataView.as_view(),
        name="delete_koujicycledata",
    ),
]
