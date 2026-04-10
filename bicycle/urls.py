from django.urls import path

from bicycle.views import display_views, operate_views, translator_views

app_name = "bicycle"
urlpatterns = [
    path("list/", display_views.BicycleSpaceListView.as_view(), name="list"),
    path("list/<int:year>/<int:month>/", display_views.BicycleSpaceListView.as_view(), name="list"),
    path("incomelist", display_views.BicycleIncomeHistoryView.as_view(), name="incomelist"),
    path("roomlist/", display_views.BicycleSpaceByRoomView.as_view(), name="roomlist"),
    path("contract_num/", display_views.BicycleSpaceFeeByRoomView.as_view(), name="contract_num"),
    path("update/<int:pk>", operate_views.BicycleSpaceUpdateView.as_view(), name="update"),
    path(
        "monthly_process/",
        operate_views.MonthlyProcessingView.as_view(),
        name="monthly_process",
    ),
    path("translator_test/", translator_views.BicycleContractImportView.as_view(), name="translator_test"),
    path("new_contract/", display_views.NewContractView.as_view(), name="new_contract"),
]
