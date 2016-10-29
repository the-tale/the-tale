# coding: utf-8

from django.conf.urls import url
from django.conf.urls import include

from dext.views import resource_patterns

from the_tale.accounts.clans.views import ClansResource, MembershipResource

urlpatterns = [url(r'^membership/', include(resource_patterns(MembershipResource), namespace='membership')),
               url(r'^', include(resource_patterns(ClansResource)) )]
