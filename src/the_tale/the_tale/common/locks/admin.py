
import smart_imports

smart_imports.all()


class LockRequestAdmin(django_admin.ModelAdmin):
    list_display = ('id', 'name', 'state', 'created_at', 'updated_at')

    list_filter = ('state', 'name')


django_admin.site.register(models.LockRequest, LockRequestAdmin)
