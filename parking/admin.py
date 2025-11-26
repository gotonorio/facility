from django.contrib import admin

from .models import ParkingSpace, ParkingType


class ParkingTypeAdmin(admin.ModelAdmin):
    list_display = ("parking_type", "rent_fee")


class ParkingSpaceAdmin(admin.ModelAdmin):
    list_display = (
        "no",
        "parking_type",
        "name",
        "room_number",
        "payment_date",
        "comment",
    )


admin.site.register(ParkingType, ParkingTypeAdmin)
admin.site.register(ParkingSpace, ParkingSpaceAdmin)
