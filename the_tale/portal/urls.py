# coding: utf-8

from django.conf.urls.defaults import patterns, include

from dext.views import resource_patterns

from the_tale.portal.views import PortalResource

urlpatterns = patterns('',
                       (r'^developers-info/', include('the_tale.portal.developers_info.urls', namespace='developers-info') ),
)

urlpatterns += resource_patterns(PortalResource)
