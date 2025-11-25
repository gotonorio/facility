from django.contrib import admin

from repair_plan_simulator.models import ConsumerPriceIndex, Shuuzenhi_income


class ShuuzenhiIncomeAdmin(admin.ModelAdmin):
    list_display = ("year", "income", "parking_income", "extra_income", "real", "comment")


admin.site.register(Shuuzenhi_income, ShuuzenhiIncomeAdmin)


class ConsumerPriceIndexAdmin(admin.ModelAdmin):
    list_display = ("year", "cpi", "comment")


admin.site.register(ConsumerPriceIndex, ConsumerPriceIndexAdmin)
