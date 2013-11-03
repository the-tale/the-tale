# coding: utf-8

from django.conf.urls.defaults import patterns, include

from dext.views import resource_patterns

from the_tale.bank.dengionline.views import DengiOnlineResource

urlpatterns = patterns('',
                       (r'^', include(resource_patterns(DengiOnlineResource))),
)
