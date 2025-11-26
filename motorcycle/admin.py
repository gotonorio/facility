from django.contrib import admin

from motorcycle.models import MotorCycleSpace


class MotorCycleSpaceAdmin(admin.ModelAdmin):
    list_display = ("no", "room_no", "date", "status_of_use", "comment")


admin.site.register(MotorCycleSpace, MotorCycleSpaceAdmin)
