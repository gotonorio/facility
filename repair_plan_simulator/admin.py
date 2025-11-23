from django.contrib import admin

from repair_plan_simulator.models import ConsumerPriceIndex


class ConsumerPriceIndexAdmin(admin.ModelAdmin):
    list_display = ("year", "cpi", "comment")


admin.site.register(ConsumerPriceIndex, ConsumerPriceIndexAdmin)
