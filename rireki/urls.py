from django.urls import path

from rireki import views

app_name = "rireki"
urlpatterns = [
    # 工事履歴の表示
    path("rireki_list/", views.RirekiListView.as_view(), name="rireki_list"),
    path("rireki_detail/<int:pk>", views.RirekiDetailView.as_view(), name="rireki_detail"),
    # データの登録
    path("create/", views.KoujiRirekiCreateView.as_view(), name="create"),
    # データの修正
    path("update_list/", views.RirekiUpdateListView.as_view(), name="update_list"),
    path(
        "update_list/<int:account_type>/<int:year>/<int:kouji_type>",
        views.RirekiUpdateListView.as_view(),
        name="update_list",
    ),
    path("update/<int:pk>/", views.RirekiUpdateView.as_view(), name="update"),
    path("delete/<int:pk>/", views.RirekiDeleteView.as_view(), name="delete"),
]
