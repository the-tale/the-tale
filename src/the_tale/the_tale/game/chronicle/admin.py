
import smart_imports

smart_imports.all()


class RecordAdmin(django_admin.ModelAdmin):
    list_display = ('id', 'type', 'created_at', 'created_at_turn', 'text')

    list_filter = ('type', )


class ActorAdmin(django_admin.ModelAdmin):
    list_display = ('id', 'uid', 'place', 'person', 'bill')


class RecordToActorAdmin(django_admin.ModelAdmin):
    list_display = ('id', 'role', 'record', 'actor')

    list_filter = ('role', )


django_admin.site.register(models.Record, RecordAdmin)
django_admin.site.register(models.RecordToActor, RecordToActorAdmin)
django_admin.site.register(models.Actor, ActorAdmin)
