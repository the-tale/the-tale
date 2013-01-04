# coding: utf-8

from dext.views import resource_patterns

from .views import BalanceResource

urlpatterns = resource_patterns(BalanceResource)
