# coding: utf-8

from django.conf.urls.defaults import patterns, include

from dext.views import resource_patterns

from the_tale.accounts.clans.views import ClansResource, MembershipResource

urlpatterns = patterns('',
                       (r'^membership/', include(resource_patterns(MembershipResource), namespace='membership')),
                       (r'^', include(resource_patterns(ClansResource)) )
    )
