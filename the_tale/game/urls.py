#coding: utf-8

from django.conf.urls.defaults import patterns, include
from dext.views.dispatcher import resource_patterns

from .views import GameResource

urlpatterns = patterns('',
                       (r'^heroes/', include('game.heroes.urls', namespace='heroes') ),
                       (r'^abilities/', include('game.abilities.urls', namespace='abilities') ),
                       (r'^map/', include('game.map.urls', namespace='map') ),
                       (r'^quests/', include('game.quests.urls', namespace='quests') ),
                       (r'^balance/', include('game.balance.urls', namespace='balance') ),
                       (r'^bills/', include('game.bills.urls', namespace='bills') ),
                       (r'^angels/', include('game.angels.urls', namespace='angels') ),
                       (r'^ratings/', include('game.ratings.urls', namespace='ratings') ),
)

urlpatterns += resource_patterns(GameResource)
