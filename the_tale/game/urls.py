#coding: utf-8

from django.conf.urls.defaults import patterns, include
from dext.views import resource_patterns

from game.views import GameResource

urlpatterns = patterns('',
                       (r'^heroes/', include('game.heroes.urls', namespace='heroes') ),
                       (r'^abilities/', include('game.abilities.urls', namespace='abilities') ),
                       (r'^map/', include('game.map.urls', namespace='map') ),
                       (r'^quests/', include('game.quests.urls', namespace='quests') ),
                       (r'^balance/', include('game.balance.urls', namespace='balance') ),
                       (r'^bills/', include('game.bills.urls', namespace='bills') ),
                       (r'^phrase-candidates/', include('game.phrase_candidates.urls', namespace='phrase-candidates') ),
                       (r'^ratings/', include('game.ratings.urls', namespace='ratings') ),
                       (r'^pvp/', include('game.pvp.urls', namespace='pvp') ),
                       (r'^mobs/', include('game.mobs.urls', namespace='mobs') ),
)

urlpatterns += resource_patterns(GameResource)
