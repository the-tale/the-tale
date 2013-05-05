# coding: utf-8

from django.contrib import admin

from bank.models import Account, Invoice

class AccountAdmin(admin.ModelAdmin):
    list_display = ('id', 'entity_type', 'entity_id', 'currency', 'created_at', 'updated_at', 'amount')
    list_filter= ('entity_type', 'currency')

class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'operation_uid', 'state', 'recipient_type', 'recipient_id', 'sender_type', 'sender_id', 'currency', 'amount', 'created_at', 'updated_at')
    list_filter= ('state', 'recipient_type', 'sender_type', 'currency')


admin.site.register(Account, AccountAdmin)
admin.site.register(Invoice, InvoiceAdmin)
