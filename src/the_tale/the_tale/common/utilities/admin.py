
import smart_imports

smart_imports.all()


class HistoryAdmin(django_admin.ModelAdmin):
    list_display = ('id', 'name', 'state', 'result', 'started_at', 'finished_at', 'created_at', 'updated_at')

    list_filter = ('state', 'result', 'name')


django_admin.site.register(models.History, HistoryAdmin)
