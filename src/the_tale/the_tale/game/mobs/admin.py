
import smart_imports

smart_imports.all()


class MobRecordAdmin(django_admin.ModelAdmin):
    list_display = ('id', 'uuid', 'name', 'archetype', 'state', 'created_at', 'updated_at')

    list_filter = ('state', 'archetype')


django_admin.site.register(models.MobRecord, MobRecordAdmin)
