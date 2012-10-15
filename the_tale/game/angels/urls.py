# coding: utf-8

from dext.views.dispatcher import resource_patterns

from game.angels.views import AngelResource

urlpatterns = resource_patterns(AngelResource)
