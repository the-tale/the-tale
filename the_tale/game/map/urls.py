# coding: utf-8

from django.conf.urls.defaults import patterns, include
from dext.views.dispatcher import resource_patterns

from .views import MapResource

urlpatterns = patterns('',
                       # (r'^roads/', include('game.map.roads.urls', namespace='roads') ),
                       (r'^places/', include('game.map.places.urls', namespace='places') ),
)

urlpatterns += resource_patterns(MapResource)
