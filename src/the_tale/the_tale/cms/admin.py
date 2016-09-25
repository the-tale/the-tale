# coding: utf-8

from django.contrib import admin
from django.db.models import Max

from the_tale.cms.models import Page


class PageAdmin(admin.ModelAdmin):

    list_display = ('caption', 'section', 'slug', 'active', 'order', 'author', 'created_at', 'editor', 'updated_at')

    readonly_fields = ('author', 'editor', 'created_at', 'updated_at')

    ordering = ('order',)

    list_filter = ('section',)

    def save_model(self, request, obj, form, change):
        if not change:
            obj.author = request.user
            obj.order = Page.objects.filter(section=obj.section).aggregate(Max('order'))['order__max']
            if obj.order is not None:
                obj.order += 1
            else:
                obj.order = 0
        else:
            obj.editor = request.user

        obj.save()

admin.site.register(Page, PageAdmin)
