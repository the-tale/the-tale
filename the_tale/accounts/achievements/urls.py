# coding: utf-8

from django.conf.urls import patterns, include

from dext.views import resource_patterns

from the_tale.accounts.achievements.views import AchievementResource, AccountAchievementsResource

urlpatterns = patterns('',
                       (r'^admin/', include(resource_patterns(AchievementResource)) ),
                       (r'^', include(resource_patterns(AccountAchievementsResource)) )
    )
