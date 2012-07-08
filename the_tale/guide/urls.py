# coding: utf-8

from dext.views.dispatcher import resource_patterns

from guide.views import GuideResource

urlpatterns = resource_patterns(GuideResource)
