# coding: utf-8

from dext.views.dispatcher import resource_patterns

from .views import PortalResource

urlpatterns = resource_patterns(PortalResource)
