
import smart_imports

smart_imports.all()


class AchievementAdmin(django_admin.ModelAdmin):
    list_display = ('id', 'approved', 'caption', 'group', 'type', 'updated_at', 'order')
    list_filter = ('approved', 'group', 'type')


class AccountAchievementsAdmin(django_admin.ModelAdmin):
    list_display = ('id', 'account')


class GiveAchievementTaskAdmin(django_admin.ModelAdmin):
    list_display = ('id', 'account', 'achievement')


django_admin.site.register(models.Achievement, AchievementAdmin)
django_admin.site.register(models.AccountAchievements, AccountAchievementsAdmin)
django_admin.site.register(models.GiveAchievementTask, GiveAchievementTaskAdmin)
