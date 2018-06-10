
from django.conf.urls import url
from django.conf.urls import include

from the_tale.game import views


urlpatterns = [url(r'^heroes/', include('the_tale.game.heroes.urls', namespace='heroes')),
               url(r'^abilities/', include('the_tale.game.abilities.urls', namespace='abilities')),
               url(r'^map/', include('the_tale.game.map.urls', namespace='map')),
               url(r'^quests/', include('the_tale.game.quests.urls', namespace='quests')),
               url(r'^balance/', include('the_tale.game.balance.urls', namespace='balance')),
               url(r'^bills/', include('the_tale.game.bills.urls', namespace='bills')),
               url(r'^ratings/', include('the_tale.game.ratings.urls', namespace='ratings')),
               url(r'^pvp/', include('the_tale.game.pvp.urls', namespace='pvp')),
               url(r'^mobs/', include('the_tale.game.mobs.urls', namespace='mobs')),
               url(r'^persons/', include('the_tale.game.persons.urls', namespace='persons')),
               url(r'^artifacts/', include('the_tale.game.artifacts.urls', namespace='artifacts')),
               url(r'^companions/', include('the_tale.game.companions.urls', namespace='companions')),
               url(r'^cards/', include('the_tale.game.cards.urls', namespace='cards')),
               url(r'^chronicle/', include('the_tale.game.chronicle.urls', namespace='chronicle')),
               url(r'^places/', include('the_tale.game.places.urls', namespace='places')),
               url(r'^politic-power/', include('the_tale.game.politic_power.urls', namespace='politic-power'))]


urlpatterns += views.resource.get_urls()
