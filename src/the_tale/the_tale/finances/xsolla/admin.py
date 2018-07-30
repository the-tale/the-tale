
import smart_imports

smart_imports.all()


class InvoiceAdmin(django_admin.ModelAdmin):
    list_display = ('id',
                    'test',
                    'state',
                    'pay_result',
                    'bank_id',
                    'bank_amount',
                    'bank_invoice',
                    'xsolla_id',
                    'xsolla_v1',
                    'xsolla_v2',
                    'xsolla_v3',
                    'updated_at',
                    'date')
    list_filter = ('state', 'pay_result', 'test')
    readonly_fields = [field.name for field in models.Invoice._meta.get_fields()]

    def has_delete_permission(self, request, obj=None):
        return False


django_admin.site.register(models.Invoice, InvoiceAdmin)
