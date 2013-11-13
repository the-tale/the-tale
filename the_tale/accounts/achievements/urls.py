# coding: utf-8

from django.conf.urls import patterns, include

from dext.views import resource_patterns

from the_tale.accounts.achievements.views import AchievementsResource

urlpatterns = patterns('',
                       (r'^', include(resource_patterns(AchievementsResource)) )
    )
