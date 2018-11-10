
import smart_imports

smart_imports.all()


class RecordAdmin(django_admin.ModelAdmin):
    list_display = ('id', 'type', 'date', 'value_int', 'value_float')
    list_filter = ('type',)


django_admin.site.register(models.Record, RecordAdmin)
