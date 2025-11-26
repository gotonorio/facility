from django.contrib import admin

from bicycle.models import BicycleSpace


class BicycleSpaceAdmin(admin.ModelAdmin):
    list_display = ("no", "location", "room_number", "date", "status_of_use", "comment")


admin.site.register(BicycleSpace, BicycleSpaceAdmin)
