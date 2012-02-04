# coding: utf-8

from dext.views.dispatcher import resource_patterns

from .views import PlaceResource

urlpatterns = resource_patterns(PlaceResource)
