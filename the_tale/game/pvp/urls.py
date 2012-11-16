# coding: utf-8

from dext.views.dispatcher import resource_patterns

from game.pvp.views import PvPResource

urlpatterns = resource_patterns(PvPResource)
