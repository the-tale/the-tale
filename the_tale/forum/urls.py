# coding: utf-8

from dext.views.dispatcher import resource_patterns

from .views import ForumResource

urlpatterns = resource_patterns(ForumResource)

