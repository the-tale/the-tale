
import smart_imports

smart_imports.all()


urlpatterns = [django_urls.url(r'^heroes/', django_urls.include(('the_tale.game.heroes.urls', 'heroes'))),
               django_urls.url(r'^abilities/', django_urls.include(('the_tale.game.abilities.urls', 'abilities'))),
               django_urls.url(r'^map/', django_urls.include(('the_tale.game.map.urls', 'map'))),
               django_urls.url(r'^quests/', django_urls.include(('the_tale.game.quests.urls', 'quests'))),
               django_urls.url(r'^balance/', django_urls.include(('the_tale.game.balance.urls', 'balance'))),
               django_urls.url(r'^bills/', django_urls.include(('the_tale.game.bills.urls', 'bills'))),
               django_urls.url(r'^ratings/', django_urls.include(('the_tale.game.ratings.urls', 'ratings'))),
               django_urls.url(r'^pvp/', django_urls.include(('the_tale.game.pvp.urls', 'pvp'))),
               django_urls.url(r'^mobs/', django_urls.include(('the_tale.game.mobs.urls', 'mobs'))),
               django_urls.url(r'^persons/', django_urls.include(('the_tale.game.persons.urls', 'persons'))),
               django_urls.url(r'^artifacts/', django_urls.include(('the_tale.game.artifacts.urls', 'artifacts'))),
               django_urls.url(r'^companions/', django_urls.include(('the_tale.game.companions.urls', 'companions'))),
               django_urls.url(r'^cards/', django_urls.include(('the_tale.game.cards.urls', 'cards'))),
               django_urls.url(r'^chronicle/', django_urls.include(('the_tale.game.chronicle.urls', 'chronicle'))),
               django_urls.url(r'^places/', django_urls.include(('the_tale.game.places.urls', 'places'))),
               django_urls.url(r'^politic-power/', django_urls.include(('the_tale.game.politic_power.urls', 'politic-power'))),
               django_urls.url(r'^emissaries/', django_urls.include(('the_tale.game.emissaries.urls', 'emissaries')))]


urlpatterns += views.resource.get_urls()
