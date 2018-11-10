
import smart_imports

smart_imports.all()


class ClanAdmin(django_admin.ModelAdmin):
    list_display = ('id', 'abbr', 'name', 'members_number', 'created_at')

    def has_delete_permission(self, request, obj=None):
        return False


class MembershipAdmin(django_admin.ModelAdmin):
    list_display = ('id', 'clan', 'account', 'role', 'created_at')

    def has_delete_permission(self, request, obj=None):
        return False


class MembershipRequestAdmin(django_admin.ModelAdmin):
    list_display = ('id', 'clan', 'account', 'type', 'initiator', 'created_at')


django_admin.site.register(models.Clan, ClanAdmin)
django_admin.site.register(models.Membership, MembershipAdmin)
django_admin.site.register(models.MembershipRequest, MembershipRequestAdmin)
