# coding: utf-8

from django.contrib import admin

from the_tale.game.bills.models import Bill, Vote, Actor


class BillAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'state', 'owner', 'updated_at', 'votes_for', 'votes_against')
    list_filter = ('state', 'type')

class ActorAdmin(admin.ModelAdmin):
    list_display = ('id', 'bill', 'place')

class VoteAdmin(admin.ModelAdmin):
    list_display = ('id', 'owner', 'type')
    list_filter = ('type',)


admin.site.register(Bill, BillAdmin)
admin.site.register(Vote, VoteAdmin)
admin.site.register(Actor, ActorAdmin)
