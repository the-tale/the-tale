
import smart_imports

smart_imports.all()


class EmissaryAdmin(django_admin.ModelAdmin):
    list_display = ('id', 'clan', 'place', 'state', 'name', 'created_at')

    list_filter = ('state', 'place')

    def name(self, obj):
        from . import logic
        return logic.load_emissary(emissary_model=obj).name


class EventAdmin(django_admin.ModelAdmin):
    list_display = ('id', 'emissary', 'state', 'stop_reason', 'created_at', 'updated_at')

    list_filter = ('state',)


django_admin.site.register(models.Emissary, EmissaryAdmin)
django_admin.site.register(models.Event, EventAdmin)
