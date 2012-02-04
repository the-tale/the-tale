# coding: utf-8

from dext.views.dispatcher import resource_patterns

from .views import NewsResource

urlpatterns = resource_patterns(NewsResource)

