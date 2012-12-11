# coding: utf-8

from dext.views.dispatcher import resource_patterns

from game.map.views import MapResource

urlpatterns = resource_patterns(MapResource)
