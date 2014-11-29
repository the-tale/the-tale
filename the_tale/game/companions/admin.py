# coding: utf-8

from django.contrib import admin

from dext.common.utils import s11n

from utg import words as utg_words

from the_tale.game.companions import models


class CompanionRecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'state', 'created_at', 'updated_at')
    list_filter = ('state',)

    def name(self, obj):
        return utg_words.Word.deserialize(s11n.from_json(obj.data)['name']).normal_form()



admin.site.register(models.CompanionRecord, CompanionRecordAdmin)
