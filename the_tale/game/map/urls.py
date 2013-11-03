# coding: utf-8

from django.conf.urls.defaults import patterns, include

from dext.views import resource_patterns

from the_tale.game.map.views import MapResource


urlpatterns = patterns('',
                       (r'^places/', include('the_tale.game.map.places.urls', namespace='places') ),
)


urlpatterns += resource_patterns(MapResource)
