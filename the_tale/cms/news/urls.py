# coding: utf-8

from dext.views import resource_patterns

from the_tale.cms.news.views import NewsResource

urlpatterns = resource_patterns(NewsResource)
