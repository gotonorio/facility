from django.contrib import admin

from control.models import ControlRecord, Description


class ControlRecordAdmin(admin.ModelAdmin):
    list_display = [
        "tmp_user_flg",
    ]


class DescriptionAdmin(admin.ModelAdmin):
    list_display = ["title", "description", "alive", "created_date"]


admin.site.register(ControlRecord, ControlRecordAdmin)
admin.site.register(Description, DescriptionAdmin)
