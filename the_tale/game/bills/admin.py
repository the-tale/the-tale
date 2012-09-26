# coding: utf-8

from django.contrib import admin

from game.bills.models import Bill


class BillAdmin(admin.ModelAdmin):
    list_display = ('id', 'state', 'owner', 'updated_at', 'votes_for', 'votes_against')

    list_filter= ('state',)


admin.site.register(Bill, BillAdmin)
