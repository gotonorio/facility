from django.urls import path

from bicycle.views import data_views, list_views

app_name = "bicycle"
urlpatterns = [
    path("list/", list_views.BicycleSpaceListView.as_view(), name="list"),
    path("list/<int:year>/<int:month>/", list_views.BicycleSpaceListView.as_view(), name="list"),
    path("roomlist/", list_views.BicycleSpaceByRoomView.as_view(), name="roomlist"),
    path("contract_num/", list_views.BicycleSpaceFeeByRoomView.as_view(), name="contract_num"),
    path("update/<int:pk>", data_views.BicycleSpaceUpdateView.as_view(), name="update"),
    path(
        "monthly_process/",
        data_views.MonthlyProcessingView.as_view(),
        name="monthly_process",
    ),
    path("export/<str:year>/<str:month>", list_views.export_bicyclefee, name="export"),
]
