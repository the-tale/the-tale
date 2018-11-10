
import smart_imports

smart_imports.all()


class CollectionAdmin(django_admin.ModelAdmin):
    list_display = ('id', 'approved', 'caption')
    list_filter = ('approved',)


class KitAdmin(django_admin.ModelAdmin):
    list_display = ('id', 'approved', 'caption', 'collection')
    list_filter = ('approved', 'collection')


class ItemAdmin(django_admin.ModelAdmin):
    list_display = ('id', 'approved', 'caption', 'kit')
    list_filter = ('approved', 'kit')


class GiveItemTaskAdmin(django_admin.ModelAdmin):
    list_display = ('id', 'account', 'item')


class AccountItemsAdmin(django_admin.ModelAdmin):
    list_display = ('id', 'account')


django_admin.site.register(models.Collection, CollectionAdmin)
django_admin.site.register(models.Kit, KitAdmin)
django_admin.site.register(models.Item, ItemAdmin)
django_admin.site.register(models.GiveItemTask, GiveItemTaskAdmin)
django_admin.site.register(models.AccountItems, AccountItemsAdmin)
