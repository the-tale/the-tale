# coding: utf-8

from dext.views.dispatcher import resource_patterns

from .views import RoadsResource

urlpatterns = resource_patterns(RoadsResource)
