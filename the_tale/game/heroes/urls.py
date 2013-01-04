# coding: utf-8

from dext.views import resource_patterns

from .views import HeroResource

urlpatterns = resource_patterns(HeroResource)
