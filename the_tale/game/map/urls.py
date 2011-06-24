from django.conf.urls.defaults import patterns, include
from django_next.views.dispatcher import resource_patterns

from .views import MapResource

urlpatterns = patterns('',
                       (r'^roads/', include('game.map.roads.urls', namespace='roads') ),
)

urlpatterns += resource_patterns(MapResource)
