
import smart_imports

smart_imports.all()


class BillAdmin(django_admin.ModelAdmin):
    list_display = ('id', 'type', 'state', 'owner', 'updated_at', 'votes_for', 'votes_against')
    list_filter = ('state', 'type')


class ActorAdmin(django_admin.ModelAdmin):
    list_display = ('id', 'bill', 'place')


class VoteAdmin(django_admin.ModelAdmin):
    list_display = ('id', 'owner', 'type')
    list_filter = ('type',)


class ModerationAdmin(django_admin.ModelAdmin):
    list_display = ('id', 'bill', 'moderator', 'created_at')


django_admin.site.register(models.Bill, BillAdmin)
django_admin.site.register(models.Vote, VoteAdmin)
django_admin.site.register(models.Actor, ActorAdmin)
django_admin.site.register(models.Moderation, ModerationAdmin)
