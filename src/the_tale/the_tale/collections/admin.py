# coding: utf-8

from django.contrib import admin

from the_tale.collections.models import Collection, Kit, Item, GiveItemTask, AccountItems


class CollectionAdmin(admin.ModelAdmin):
    list_display = ('id', 'approved', 'caption')
    list_filter = ('approved',)


class KitAdmin(admin.ModelAdmin):
    list_display = ('id', 'approved', 'caption', 'collection')
    list_filter = ('approved', 'collection')


class ItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'approved', 'caption', 'kit')
    list_filter = ('approved', 'kit')


class GiveItemTaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'account', 'item')

class AccountItemsAdmin(admin.ModelAdmin):
    list_display = ('id', 'account')


admin.site.register(Collection, CollectionAdmin)
admin.site.register(Kit, KitAdmin)
admin.site.register(Item, ItemAdmin)
admin.site.register(GiveItemTask, GiveItemTaskAdmin)
admin.site.register(AccountItems, AccountItemsAdmin)
