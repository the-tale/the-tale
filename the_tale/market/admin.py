# coding: utf-8

from django.contrib import admin

from the_tale.market import models


class LotAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'state', 'good_uid', 'price', 'seller', 'buyer', 'created_at')
    list_filter = ('type', 'state',)


class GoodsAdmin(admin.ModelAdmin):
    list_display = ('id', 'account', 'created_at')


admin.site.register(models.Lot, LotAdmin)
admin.site.register(models.Goods, GoodsAdmin)
