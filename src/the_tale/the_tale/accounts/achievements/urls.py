# coding: utf-8

from django.conf.urls import url
from django.conf.urls import include

from dext.views import resource_patterns

from the_tale.accounts.achievements.views import AchievementsResource

urlpatterns = [url(r'^', include(resource_patterns(AchievementsResource)) )]
