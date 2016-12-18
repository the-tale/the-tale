# coding: utf-8

from django.contrib import admin

from the_tale.cms.news.models import News

class NewsAdmin(admin.ModelAdmin):
    list_display = ('id', 'caption', 'emailed', 'created_at')

    readonly_fields = ('forum_thread',)


admin.site.register(News, NewsAdmin)
