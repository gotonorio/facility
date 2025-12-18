from django.urls import path

from repair_plan.views import data_views, list_views, master_data_views, table_views

app_name = "repair_plan"
urlpatterns = [
    # マスタープランの表示
    path(
        "masterplan_list/",
        master_data_views.MasterPlanListView.as_view(),
        name="masterplan_list",
    ),
    # 修繕計画のリスト表示
    path(
        "repairplan_list/",
        list_views.RepairPlanListView.as_view(),
        name="repairplan_list",
    ),
    # 年度別修繕計画の表示
    path(
        "repairplan_by_year/<int:year>/<int:ver>",
        list_views.RepairPlanByYearView.as_view(),
        name="repairplan_by_year",
    ),
    # 工事種別別修繕計画の表示
    path(
        "repairplan_by_koujitype/",
        list_views.RepairPlanByKoujitypeView.as_view(),
        name="repairplan_by_koujitype",
    ),
    # 修繕計画のテーブル表示
    path(
        "repairplan_table/",
        table_views.RepairPlanTableView.as_view(),
        name="repairplan_table",
    ),
    # 簡易版修繕計画表の表示
    path(
        "repairplan_simpletable/",
        table_views.RepairPlanSimpleTableView.as_view(),
        name="repairplan_simpletable",
    ),
    # マスタデータの登録
    path(
        "create_master_plan/",
        data_views.MasterPlanCreateView.as_view(),
        name="create_master_plan",
    ),
    # 修繕計画データの登録
    path(
        "add_repair_plan/",
        data_views.ReparPlanCreateView.as_view(),
        name="add_repair_plan",
    ),
    # 計画初年度の修繕費会計残高の修正
    path(
        "update_master_plan/<int:pk>",
        data_views.MasterPlanUpdateView.as_view(),
        name="update_master_plan",
    ),
    # 長期修繕計画のデータ編集用一覧表
    path(
        "repairplan_update_list/",
        data_views.RepairPlanUpdateListView.as_view(),
        name="repairplan_update_list",
    ),
    path(
        "repairplan_update/<int:pk>",
        data_views.RepairPlanUpdateView.as_view(),
        name="repairplan_update",
    ),
    # 修繕計画のデータ削除
    path(
        "delete_repair_plan/<int:pk>",
        data_views.RepairPlanDeleteView.as_view(),
        name="delete_repair_plan",
    ),
    # バージョンごとの修繕計画データ一括削除
    path(
        "delete_koujiname_ver/",
        data_views.KoujiNameDeleteView.as_view(),
        name="delete_koujiname_ver",
    ),
    # 修繕計画マスターデータの削除
    path(
        "delete_master_plan/<int:pk>/",
        master_data_views.MasterPlanDeleteView.as_view(),
        name="delete_master_plan",
    ),
    # データ複製
    path(
        "duplicate_repair_plan/",
        data_views.RepairPlanDuplicateView.as_view(),
        name="duplicate_repair_plan",
    ),
    # 修繕計画マスタデータの作成
    path(
        "create_koujitype/",
        master_data_views.KoujiTypeCreateView.as_view(),
        name="create_koujitype",
    ),
    path(
        "update_koujitype/<int:pk>",
        master_data_views.KoujiTypeUpdateView.as_view(),
        name="update_koujitype",
    ),
    path(
        "create_unitname/",
        master_data_views.MasterUnitCreateView.as_view(),
        name="create_unitname",
    ),
    # 長期修繕計画データのインポート
    path(
        "import_repair_plan/",
        master_data_views.RepairPlanImportView.as_view(),
        name="import_repair_plan",
    ),
]
