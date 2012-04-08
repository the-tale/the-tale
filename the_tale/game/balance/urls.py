# coding: utf-8

from dext.views.dispatcher import resource_patterns

from .views import BalanceResource

urlpatterns = resource_patterns(BalanceResource)
