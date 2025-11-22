from django.urls import path

from repair_plan.views import data_views, list_views, master_data_views, table_views

app_name = "repair_plan"
urlpatterns = [
    # マスタープランの表示
    path(
        "repair_masterplan_list/",
        master_data_views.MasterPlanListView.as_view(),
        name="repair_masterplan_list",
    ),
    # 修繕計画のリスト表示
    path(
        "repair_plan_list/",
        list_views.RepairPlanListView.as_view(),
        name="repair_plan_list",
    ),
    path(
        "repair_plan_by_year/<int:year>/<int:ver>",
        list_views.RepairPlanByYearView.as_view(),
        name="repair_plan_by_year",
    ),
    path(
        "repair_plan_by_koujitype/",
        list_views.RepairPlanByKoujitypeView.as_view(),
        name="repair_plan_by_koujitype",
    ),
    # 修繕計画のテーブル表示
    path(
        "repair_plan_table/",
        table_views.RepairPlanTableView.as_view(),
        name="repair_plan_table",
    ),
    path(
        "repair_plan_simpletable/",
        table_views.RepairPlanSimpleTableView.as_view(),
        name="repair_plan_simpletable",
    ),
    # データの登録
    path(
        "create_master_plan/",
        data_views.MasterPlanCreateView.as_view(),
        name="create_master_plan",
    ),
    path(
        "add_repair_plan/",
        data_views.CreateRepairPlanView.as_view(),
        name="add_repair_plan",
    ),
    # データの修正
    path(
        "update_master_plan/<int:pk>",
        data_views.MasterPlanUpdateView.as_view(),
        name="update_master_plan",
    ),
    path(
        "update_repair_plan_list/",
        data_views.UpdateRepairPlanListView.as_view(),
        name="update_repair_plan_list",
    ),
    path(
        "update_repair_plan_list/<int:version>/<int:kouji_type>",
        data_views.UpdateRepairPlanListView.as_view(),
        name="update_repair_plan_list",
    ),
    path(
        "update_repair_plan/<int:pk>",
        data_views.UpdateRepairPlanView.as_view(),
        name="update_repair_plan",
    ),
    # データ削除
    path(
        "delete_repair_plan/<int:pk>",
        data_views.DeleteRepairPlanView.as_view(),
        name="delete_repair_plan",
    ),
    path(
        "delete_koujiname_ver/",
        data_views.DeleteKoujiNameByVerView.as_view(),
        name="delete_koujiname_ver",
    ),
    # データ複製
    path(
        "duplicate_repair_plan/",
        data_views.DuplicateRepairPlanView.as_view(),
        name="duplicate_repair_plan",
    ),
    # マスタデータの作成
    path(
        "create_koujitype/",
        master_data_views.CreateKoujiTypeView.as_view(),
        name="create_koujitype",
    ),
    path(
        "update_koujitype/<int:pk>",
        master_data_views.UpdateKoujiTypeView.as_view(),
        name="update_koujitype",
    ),
    path(
        "create_unitname/",
        master_data_views.CreateMasterUnitView.as_view(),
        name="create_unitname",
    ),
    # 長期修繕計画データのインポート
    path(
        "import_repair_plan/",
        master_data_views.ImportRepairPlanDataView.as_view(),
        name="import_repair_plan",
    ),
]
