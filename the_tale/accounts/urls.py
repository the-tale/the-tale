# coding: utf-8

from dext.views.dispatcher import resource_patterns

from .views import AccountsResource

urlpatterns = resource_patterns(AccountsResource)
