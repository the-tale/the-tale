# coding: utf-8

from dext.views import resource_patterns

from the_tale.game.balance.views import BalanceResource

urlpatterns = resource_patterns(BalanceResource)
