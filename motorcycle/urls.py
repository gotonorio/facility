from django.urls import path

from motorcycle.views import data_views, motorcyclelist_views

app_name = "motorcycle"
urlpatterns = [
    path("list/", motorcyclelist_views.MotorCycleSpaceListView.as_view(), name="list"),
    path("list/<int:year>/<int:month>/", motorcyclelist_views.MotorCycleSpaceListView.as_view(), name="list"),
    path(
        "monthly_process/",
        data_views.MonthlyProcessingView.as_view(),
        name="monthly_process",
    ),
    path("update/<int:pk>", data_views.MotorCycleSpaceUpdateView.as_view(), name="update"),
]
