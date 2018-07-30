
import smart_imports

smart_imports.all()


class ArtifactRecordAdmin(django_admin.ModelAdmin):
    list_display = ('id', 'uuid', 'name', 'state', 'type', 'power_type', 'created_at', 'updated_at')

    list_filter = ('state', 'type', 'power_type')


django_admin.site.register(models.ArtifactRecord, ArtifactRecordAdmin)
