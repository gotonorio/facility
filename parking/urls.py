from django.urls import path

from parking.views import data_views, parkinglist_views

app_name = "parking"
urlpatterns = [
    # ユーザ用
    path("list/", parkinglist_views.ParkingSpaceListView.as_view(), name="list"),
    path("rirekilist", parkinglist_views.IncomeRirekiView.as_view(), name="rirekilist"),
    path("export/<str:year>", parkinglist_views.export_parkingfee, name="export_parkingfee"),
    path("fig/", parkinglist_views.ParkingFigView.as_view(), name="fig"),
    path("fig/<int:year>/<int:month>/", parkinglist_views.ParkingFigView.as_view(), name="fig"),
    path(
        "utilization_rate/",
        parkinglist_views.UtilizationRateView.as_view(),
        name="utilization_rate",
    ),
    # 管理者用
    path("management/", parkinglist_views.ParkingSpaceManagementView.as_view(), name="management"),
    path("monthly/", data_views.MonthlyProcessingView.as_view(), name="monthly"),
    path("update/<int:pk>", data_views.ParkingUpdateView.as_view(), name="update"),
]
