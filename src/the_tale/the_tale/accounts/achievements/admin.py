# coding: utf-8

from django.contrib import admin

from the_tale.accounts.achievements.models import Achievement, AccountAchievements, GiveAchievementTask


class AchievementAdmin(admin.ModelAdmin):
    list_display = ('id', 'approved', 'caption', 'group', 'type', 'updated_at', 'order')
    list_filter = ('approved', 'group', 'type')


class AccountAchievementsAdmin(admin.ModelAdmin):
    list_display = ('id', 'account')


class GiveAchievementTaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'account', 'achievement')


admin.site.register(Achievement, AchievementAdmin)
admin.site.register(AccountAchievements, AccountAchievementsAdmin)
admin.site.register(GiveAchievementTask, GiveAchievementTaskAdmin)
