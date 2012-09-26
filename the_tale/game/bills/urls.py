# coding: utf-8

from dext.views.dispatcher import resource_patterns

from game.bills.views import BillResource

urlpatterns = resource_patterns(BillResource)
