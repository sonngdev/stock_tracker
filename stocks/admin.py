from django.contrib import admin

from .models import Stock, DiscountedCashflowData

admin.site.register(Stock)
admin.site.register(DiscountedCashflowData)
