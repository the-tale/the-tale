
import smart_imports

smart_imports.all()


class MessageAdmin(django_admin.ModelAdmin):
    list_display = ('id', 'state', 'created_at')
    list_filter = ('state',)


django_admin.site.register(models.Message, MessageAdmin)
