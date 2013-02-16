# coding: utf-8

from django.conf.urls.defaults import patterns, include

from dext.views import resource_patterns

from portal.views import PortalResource

urlpatterns = patterns('',
                       (r'^developers-info/', include('portal.developers_info.urls', namespace='developers-info') ),
)

urlpatterns += resource_patterns(PortalResource)
