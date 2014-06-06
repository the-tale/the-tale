# coding: utf-8

from dext.views import resource_patterns

from the_tale.game.cards.views import CardsResource

urlpatterns = resource_patterns(CardsResource)
