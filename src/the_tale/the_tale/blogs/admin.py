# coding: utf-8

from django.contrib import admin

from the_tale.blogs import models


class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'caption', 'votes', 'rating', 'author', 'state', 'moderator', 'created_at', 'updated_at')

class VoteAdmin(admin.ModelAdmin):
    list_display = ('id', 'voter', 'post', 'created_at')

class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description', 'created_at', 'updated_at')

class TaggedAdmin(admin.ModelAdmin):
    list_display = ('id', 'post', 'tag', 'created_at', 'updated_at')


admin.site.register(models.Post, PostAdmin)
admin.site.register(models.Vote, VoteAdmin)
admin.site.register(models.Tag, TagAdmin)
admin.site.register(models.Tagged, TaggedAdmin)
