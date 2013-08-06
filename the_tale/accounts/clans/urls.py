# coding: utf-8

from dext.views import resource_patterns

from accounts.clans.views import ClansResource

urlpatterns = resource_patterns(ClansResource)
