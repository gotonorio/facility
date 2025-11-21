from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


# Register your models here.
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        "username",
        "email",
        "is_active",
        "is_deleted",
        "deleted_at",
        "is_staff",
    )

    list_filter = ("is_staff", "is_deleted", "is_superuser")

    # 論理削除ユーザーを Admin 一覧にも表示するために override
    def get_queryset(self, request):
        return User.all_objects.all()  # 後述の "all_objects" Manager を使用
