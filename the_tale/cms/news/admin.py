# coding: utf-8

from django.contrib import admin
from django.core.urlresolvers import reverse

from the_tale.cms.news.models import News

class NewsAdmin(admin.ModelAdmin):
    list_display = ('id', 'caption', 'created_at', 'publish_on_forum')

    readonly_fields = ('forum_thread',)

    def publish_on_forum(self, obj):
        if obj.forum_thread is None:
            return '<a href="%s">опубликовать</a>' % reverse('news:publish-on-forum', args=[obj.id] )
        return '<a href="%s">перейти</a>' % obj.forum_thread.get_absolute_url()
    publish_on_forum.short_description = u'Форум'
    publish_on_forum.allow_tags = True

admin.site.register(News, NewsAdmin)
