# coding: utf-8

from django.contrib import admin

from the_tale.finances.bank.models import Account, Invoice

class AccountAdmin(admin.ModelAdmin):
    list_display = ('id', 'entity_type', 'entity_id', 'currency', 'created_at', 'updated_at', 'amount')
    list_filter = ('entity_type', 'currency')
    readonly_fields = [field.name for field in Account._meta.get_fields()]

    def has_delete_permission(self, request, obj=None):
        return False

class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'operation_uid', 'state', 'recipient_type', 'recipient_id', 'sender_type', 'sender_id', 'currency', 'amount', 'created_at', 'updated_at')
    list_filter = ('state', 'recipient_type', 'sender_type', 'currency')
    readonly_fields = [field.name for field in Invoice._meta.get_fields()]

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(Account, AccountAdmin)
admin.site.register(Invoice, InvoiceAdmin)
