import smart_imports

smart_imports.all()


class SettingAdmin(django_admin.ModelAdmin):
    list_display = ('key', 'value', 'updated_at')

    def save_model(self, request, obj, form, change):
        from .settings import settings
        settings[obj.key] = obj.value

    def delete_model(self, request, obj):
        from .settings import settings
        del settings[obj.key]


django_admin.site.register(models.Setting, SettingAdmin)
