# Register your models here.

from django.contrib import admin

from repair_plan.models import KoujiName, MasterKoujiType, MasterPlan, MasterUnit


class MasterPlanAdmin(admin.ModelAdmin):
    list_display = ("version", "first_year", "final_year", "balance", "comment")


class MasterKoujiTypeAdmin(admin.ModelAdmin):
    list_display = (
        "sequense",
        "master_name",
    )


class MasterUnitAdmin(admin.ModelAdmin):
    list_display = ("unit_name",)


class KoujiNameAdmin(admin.ModelAdmin):
    list_display = (
        "version",
        "kouji_type",
        "kouji_name",
        "kouji_spec",
        "kouji_quantity",
        "unit",
        "unit_price",
        "kouji_year",
        "comment",
        "complete",
    )


admin.site.register(MasterPlan, MasterPlanAdmin)
admin.site.register(MasterKoujiType, MasterKoujiTypeAdmin)
admin.site.register(MasterUnit, MasterUnitAdmin)
admin.site.register(KoujiName, KoujiNameAdmin)
