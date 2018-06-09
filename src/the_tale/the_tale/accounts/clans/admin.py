
from django.contrib import admin

from the_tale.accounts.clans.models import Clan, Membership, MembershipRequest


class ClanAdmin(admin.ModelAdmin):
    list_display = ('id', 'abbr', 'name', 'members_number', 'created_at')

    def has_delete_permission(self, request, obj=None):
        return False


class MembershipAdmin(admin.ModelAdmin):
    list_display = ('id', 'clan', 'account', 'role', 'created_at')

    def has_delete_permission(self, request, obj=None):
        return False


class MembershipRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'clan', 'account', 'type', 'initiator', 'created_at')


admin.site.register(Clan, ClanAdmin)
admin.site.register(Membership, MembershipAdmin)
admin.site.register(MembershipRequest, MembershipRequestAdmin)
