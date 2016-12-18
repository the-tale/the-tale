# coding: utf-8

from django.contrib import admin

from the_tale.finances.market import models


class LotAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'state', 'good_uid', 'price', 'commission', 'seller', 'buyer', 'created_at', 'closed_at')
    list_filter = ('type', 'state',)


class GoodsAdmin(admin.ModelAdmin):
    list_display = ('id', 'account', 'created_at')


admin.site.register(models.Lot, LotAdmin)
admin.site.register(models.Goods, GoodsAdmin)
