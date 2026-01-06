from django.urls import path

from parking.views import display_views, operate_views

app_name = "parking"
urlpatterns = [
    # ユーザ用
    path("list/", display_views.ParkingSpaceListView.as_view(), name="list"),
    path("rirekilist", display_views.IncomeRirekiView.as_view(), name="rirekilist"),
    # path("rirekilist", parkinglist_views.UtilizationRateView.as_view(), name="rirekilist"),
    path("fig/", display_views.ParkingFigView.as_view(), name="fig"),
    path("fig/<int:year>/<int:month>/", display_views.ParkingFigView.as_view(), name="fig"),
    path(
        "utilization_rate/",
        display_views.UtilizationRateView.as_view(),
        name="utilization_rate",
    ),
    # 管理者用
    path("management/", display_views.ParkingSpaceManagementView.as_view(), name="management"),
    path("monthly/", operate_views.MonthlyProcessingView.as_view(), name="monthly"),
    path("update/<int:pk>", operate_views.ParkingUpdateView.as_view(), name="update"),
]
