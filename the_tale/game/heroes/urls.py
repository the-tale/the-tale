# coding: utf-8

from dext.views import resource_patterns

from the_tale.game.heroes.views import HeroResource

urlpatterns = resource_patterns(HeroResource)
