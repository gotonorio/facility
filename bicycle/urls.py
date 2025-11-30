from django.urls import path

from bicycle.views import bicyclelist_views, data_views

app_name = "bicycle"
urlpatterns = [
    path("list/", bicyclelist_views.BicycleSpaceListView.as_view(), name="list"),
    path("list/<int:year>/<int:month>/", bicyclelist_views.BicycleSpaceListView.as_view(), name="list"),
    path("incomelist", bicyclelist_views.BicycleIncomeHistoryView.as_view(), name="incomelist"),
    path("roomlist/", bicyclelist_views.BicycleSpaceByRoomView.as_view(), name="roomlist"),
    path("contract_num/", bicyclelist_views.BicycleSpaceFeeByRoomView.as_view(), name="contract_num"),
    path("update/<int:pk>", data_views.BicycleSpaceUpdateView.as_view(), name="update"),
    path(
        "monthly_process/",
        data_views.MonthlyProcessingView.as_view(),
        name="monthly_process",
    ),
    path("export/<str:year>/<str:month>", bicyclelist_views.export_bicyclefee, name="export"),
]
