# coding: utf-8

from django.conf.urls.defaults import patterns, include

from dext.views.dispatcher import resource_patterns

from portal.views import PortalResource, UserResource

urlpatterns = patterns('',
                       (r'^users/', include(resource_patterns(UserResource), namespace='users') )
    )

urlpatterns += resource_patterns(PortalResource)
