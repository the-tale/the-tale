# coding: utf-8

from dext.views import resource_patterns

from the_tale.game.bills.views import BillResource

urlpatterns = resource_patterns(BillResource)
