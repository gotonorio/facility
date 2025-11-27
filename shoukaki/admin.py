from django.contrib import admin

from .models import Shoukaki, ShoukakiType


class ShoukakiTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "shoukaki_type", "keisiki", "valid_period", "price")


class ShoukakiAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "shoukaki",
        "installation_date",
        "inspection_date",
        "location",
        "made_year",
        "made_no",
        "alive",
        "comment",
    )


admin.site.register(ShoukakiType, ShoukakiTypeAdmin)
admin.site.register(Shoukaki, ShoukakiAdmin)
