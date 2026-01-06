from django.urls import path

from motorcycle.views import display_views, operate_views

app_name = "motorcycle"
urlpatterns = [
    path("list/", display_views.MotorCycleSpaceListView.as_view(), name="list"),
    path("list/<int:year>/<int:month>/", display_views.MotorCycleSpaceListView.as_view(), name="list"),
    path(
        "monthly_process/",
        operate_views.MonthlyProcessingView.as_view(),
        name="monthly_process",
    ),
    path("update/<int:pk>", operate_views.MotorCycleSpaceUpdateView.as_view(), name="update"),
]
