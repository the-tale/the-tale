
import smart_imports

smart_imports.all()


class FriendshipAdmin(django_admin.ModelAdmin):
    list_display = ('id', 'friend_1', 'friend_2', 'is_confirmed')
    list_filter = ('is_confirmed',)


django_admin.site.register(models.Friendship, FriendshipAdmin)
