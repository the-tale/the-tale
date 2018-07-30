
import smart_imports

smart_imports.all()


class PostponedTaskAdmin(django_admin.ModelAdmin):
    list_display = ('id', 'state', 'internal_type', 'internal_state', 'created_at', 'live_time')
    list_filter = ('state', 'internal_state', 'internal_type')


django_admin.site.register(models.PostponedTask, PostponedTaskAdmin)
