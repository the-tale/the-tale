# coding: utf-8

from django.conf.urls import patterns, include

from dext.views import resource_patterns

from the_tale.accounts.third_party.views import TokensResource

urlpatterns = patterns('',
                       (r'^tokens/', include(resource_patterns(TokensResource), namespace='tokens'))
    )
