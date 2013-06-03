# coding: utf-8

from django.contrib import admin

from bank.dengionline.models import Invoice

class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('id',
                    'user_id',
                    'state',
                    'bank_type',
                    'bank_id',
                    'bank_currency',
                    'bank_amount',
                    'payment_amount',
                    'payment_currency',
                    'received_amount',
                    'received_currency',
                    'created_at',
                    'updated_at')
    list_filter= ('state', 'bank_type', 'payment_currency', 'received_currency')
    readonly_fields = Invoice._meta.get_all_field_names()

    def has_delete_permission(self, request, obj=None):
        return False

admin.site.register(Invoice, InvoiceAdmin)
