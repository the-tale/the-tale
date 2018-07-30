
import smart_imports

smart_imports.all()


class AccountAdmin(django_admin.ModelAdmin):
    list_display = ('id', 'entity_type', 'entity_id', 'currency', 'created_at', 'updated_at', 'amount')
    list_filter = ('entity_type', 'currency')
    readonly_fields = [field.name for field in models.Account._meta.get_fields()]

    def has_delete_permission(self, request, obj=None):
        return False


class InvoiceAdmin(django_admin.ModelAdmin):
    list_display = ('id', 'operation_uid', 'state', 'recipient_type', 'recipient_id', 'sender_type', 'sender_id', 'currency', 'amount', 'created_at', 'updated_at')
    list_filter = ('state', 'recipient_type', 'sender_type', 'currency')
    readonly_fields = [field.name for field in models.Invoice._meta.get_fields()]

    def has_delete_permission(self, request, obj=None):
        return False


django_admin.site.register(models.Account, AccountAdmin)
django_admin.site.register(models.Invoice, InvoiceAdmin)
