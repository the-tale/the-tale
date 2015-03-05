#coding: utf-8

from django.conf.urls import patterns, include

from the_tale.game import views

urlpatterns = patterns('',
                       (r'^heroes/', include('the_tale.game.heroes.urls', namespace='heroes') ),
                       (r'^abilities/', include('the_tale.game.abilities.urls', namespace='abilities') ),
                       (r'^map/', include('the_tale.game.map.urls', namespace='map') ),
                       (r'^quests/', include('the_tale.game.quests.urls', namespace='quests') ),
                       (r'^balance/', include('the_tale.game.balance.urls', namespace='balance') ),
                       (r'^bills/', include('the_tale.game.bills.urls', namespace='bills') ),
                       (r'^ratings/', include('the_tale.game.ratings.urls', namespace='ratings') ),
                       (r'^pvp/', include('the_tale.game.pvp.urls', namespace='pvp') ),
                       (r'^mobs/', include('the_tale.game.mobs.urls', namespace='mobs') ),
                       (r'^artifacts/', include('the_tale.game.artifacts.urls', namespace='artifacts') ),
                       (r'^companions/', include('the_tale.game.companions.urls', namespace='companions') ),
                       (r'^cards/', include('the_tale.game.cards.urls', namespace='cards') ),
                       (r'^chronicle/', include('the_tale.game.chronicle.urls', namespace='chronicle') ),
)

urlpatterns += views.resource.get_urls()
