
import smart_imports

smart_imports.all()


class Battle1x1Admin(django_admin.ModelAdmin):
    list_display = ('id', 'state', 'calculate_rating', 'account', 'enemy', 'created_at')

    list_filter = ('state',)


class Battle1x1ResultAdmin(django_admin.ModelAdmin):
    list_display = ('id', 'participant_1', 'participant_2', 'result', 'created_at')
    list_filter = ('result',)


django_admin.site.register(models.Battle1x1, Battle1x1Admin)
django_admin.site.register(models.Battle1x1Result, Battle1x1ResultAdmin)
