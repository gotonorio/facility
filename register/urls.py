from django.urls import path

from register.views import user_views, views

"""
https://torina.top/detail/222/
"""
app_name = "register"
urlpatterns = [
    path("", views.Login.as_view(), name="login"),
    path("login/", views.Login.as_view(), name="login"),
    path("logout/", views.Logout.as_view(), name="logout"),
    # メインページ
    path("mypage", views.MypageView.as_view(), name="mypage"),
    # 設備台帳メインページ
    path("facility", views.FacilityView.as_view(), name="facility"),
    # 長期修繕計画メインページ
    path("repair_plan", views.RepairPlanView.as_view(), name="repair_plan"),
    # 長期修繕計画データ管理ページ
    path("repair_plan_data", views.RepairPlanDataView.as_view(), name="repair_plan_data"),
    # ユーザー操作
    path("signup", user_views.TempUserCreateView.as_view(), name="signup"),
    path("signup_done", user_views.TempUserDoneView.as_view(), name="temp_user_done"),
    path("user_list", user_views.UserListView.as_view(), name="user_list"),
    path(
        "user_update/<int:pk>/",
        user_views.UserManagementView.as_view(),
        name="user_update",
    ),
    path(
        "pwd_update/<int:pk>/",
        user_views.UserPasswordUpdate.as_view(),
        name="pwd_update",
    ),
    path("delete_user/<int:pk>", user_views.DeleteUserView.as_view(), name="delete_user"),
]
