# coding: utf-8

from django.conf.urls import url
from django.conf.urls import include

from dext.views import resource_patterns

from the_tale.portal.views import PortalResource

urlpatterns = [url(r'^developers-info/', include('the_tale.portal.developers_info.urls', namespace='developers-info') )]

urlpatterns += resource_patterns(PortalResource)
