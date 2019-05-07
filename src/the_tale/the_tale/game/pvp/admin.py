
import smart_imports

smart_imports.all()


class Battle1x1ResultAdmin(django_admin.ModelAdmin):
    list_display = ('id', 'participant_1', 'participant_2', 'result', 'created_at')
    list_filter = ('result',)


django_admin.site.register(models.Battle1x1Result, Battle1x1ResultAdmin)
