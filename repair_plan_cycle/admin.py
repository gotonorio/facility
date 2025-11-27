from django.contrib import admin

from repair_plan_cycle.models import KoujiCycleData


class KoujiCycleDataAdmin(admin.ModelAdmin):
    list_display = (
        "version",
        "kouji_type",
        "kouji_name",
        "first_year",
        "repeat_cycle",
        "cost",
        "comment",
    )


admin.site.register(KoujiCycleData, KoujiCycleDataAdmin)
