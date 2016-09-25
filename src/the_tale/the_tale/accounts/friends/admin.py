# coding: utf-8

from django.contrib import admin


from the_tale.accounts.friends.models import Friendship

class FriendshipAdmin(admin.ModelAdmin):
    list_display = ('id', 'friend_1', 'friend_2', 'is_confirmed')
    list_filter = ('is_confirmed',)

admin.site.register(Friendship, FriendshipAdmin)
