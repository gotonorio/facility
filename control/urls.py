from django.urls import path

from control import views

app_name = "control"
urlpatterns = [
    path("control_list", views.ControlRecordListView.as_view(), name="control_list"),
    path("description/", views.DescriptionView.as_view(), name="description"),
    # 仮登録メニュー表示のON/OFF切替え
    path(
        "control_update/<int:pk>/",
        views.ControlRecordUpdateView.as_view(),
        name="control_update",
    ),
    # 説明書の作成・修正・削除
    path(
        "description_create/",
        views.DescriptionCreateView.as_view(),
        name="description_create",
    ),
    path(
        "description_update/<int:pk>",
        views.DescriptionUpdateView.as_view(),
        name="description_update",
    ),
    path(
        "description_delete/<int:pk>",
        views.DescriptionDeleteView.as_view(),
        name="description_delete",
    ),
    # DBバックアップ処理
    path("backup/", views.backupDB, name="backupDB"),
]
