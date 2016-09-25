# coding: utf-8

from dext.views import resource_patterns

from the_tale.game.mobs.views import GameMobResource

urlpatterns = resource_patterns(GameMobResource)
