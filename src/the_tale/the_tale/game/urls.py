
import smart_imports

smart_imports.all()


urlpatterns = [django_urls.url(r'^heroes/', django_urls.include('the_tale.game.heroes.urls', namespace='heroes')),
               django_urls.url(r'^abilities/', django_urls.include('the_tale.game.abilities.urls', namespace='abilities')),
               django_urls.url(r'^map/', django_urls.include('the_tale.game.map.urls', namespace='map')),
               django_urls.url(r'^quests/', django_urls.include('the_tale.game.quests.urls', namespace='quests')),
               django_urls.url(r'^balance/', django_urls.include('the_tale.game.balance.urls', namespace='balance')),
               django_urls.url(r'^bills/', django_urls.include('the_tale.game.bills.urls', namespace='bills')),
               django_urls.url(r'^ratings/', django_urls.include('the_tale.game.ratings.urls', namespace='ratings')),
               django_urls.url(r'^pvp/', django_urls.include('the_tale.game.pvp.urls', namespace='pvp')),
               django_urls.url(r'^mobs/', django_urls.include('the_tale.game.mobs.urls', namespace='mobs')),
               django_urls.url(r'^persons/', django_urls.include('the_tale.game.persons.urls', namespace='persons')),
               django_urls.url(r'^artifacts/', django_urls.include('the_tale.game.artifacts.urls', namespace='artifacts')),
               django_urls.url(r'^companions/', django_urls.include('the_tale.game.companions.urls', namespace='companions')),
               django_urls.url(r'^cards/', django_urls.include('the_tale.game.cards.urls', namespace='cards')),
               django_urls.url(r'^chronicle/', django_urls.include('the_tale.game.chronicle.urls', namespace='chronicle')),
               django_urls.url(r'^places/', django_urls.include('the_tale.game.places.urls', namespace='places')),
               django_urls.url(r'^politic-power/', django_urls.include('the_tale.game.politic_power.urls', namespace='politic-power'))]


urlpatterns += views.resource.get_urls()
