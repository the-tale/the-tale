# coding: utf-8

from django.contrib import admin

from game.bills.models import Bill, Vote


class BillAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'state', 'owner', 'updated_at', 'votes_for', 'votes_against')

    list_filter= ('state', 'type')


class VoteAdmin(admin.ModelAdmin):
    list_display = ('id', 'owner', 'value')
    list_filter= ('value',)


admin.site.register(Bill, BillAdmin)
admin.site.register(Vote, VoteAdmin)
