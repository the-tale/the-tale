# coding: utf-8

from django.contrib import admin

from the_tale.game.chronicle.models import Record, Actor, RecordToActor


class RecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'created_at', 'created_at_turn', 'text')

    list_filter = ('type', )

class ActorAdmin(admin.ModelAdmin):
    list_display = ('id', 'uid', 'place', 'person', 'bill')

class RecordToActorAdmin(admin.ModelAdmin):
    list_display = ('id', 'role', 'record', 'actor')

    list_filter = ('role', )

admin.site.register(Record, RecordAdmin)
admin.site.register(RecordToActor, RecordToActorAdmin)
admin.site.register(Actor, ActorAdmin)
