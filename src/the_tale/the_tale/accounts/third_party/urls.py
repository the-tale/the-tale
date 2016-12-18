# coding: utf-8

from django.conf.urls import url
from django.conf.urls import include

from dext.views import resource_patterns

from the_tale.accounts.third_party.views import TokensResource

urlpatterns = [ url(r'^tokens/', include(resource_patterns(TokensResource), namespace='tokens'))]
