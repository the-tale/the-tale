#coding: utf-8

from django.conf.urls.defaults import patterns, include
from django_next.views.dispatcher import resource_patterns

from .views import GameResource

urlpatterns = patterns('',
                       (r'^angels/', include('game.angels.urls', namespace='angels') ),
                       (r'^heroes/', include('game.heroes.urls', namespace='heroes') ),
                       (r'^abilities/', include('game.abilities.urls', namespace='abilities') ),
                       (r'^journal_messages/', include('game.journal_messages.urls', namespace='journal_messages') ),
                       (r'^map/', include('game.map.urls', namespace='map') ),
                       (r'^quests/', include('game.quests.urls', namespace='quests') ),
)

urlpatterns += resource_patterns(GameResource)
