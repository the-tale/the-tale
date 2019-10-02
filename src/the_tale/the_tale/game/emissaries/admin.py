
import smart_imports

smart_imports.all()


class EmissaryAdmin(django_admin.ModelAdmin):
    list_display = ('id', 'clan', 'place', 'state', 'name', 'created_at')

    list_filter = ('state', 'place')

    def name(self, obj):
        from . import logic
        return logic.load_emissary(emissary_model=obj).name


django_admin.site.register(models.Emissary, EmissaryAdmin)
