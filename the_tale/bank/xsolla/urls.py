# coding: utf-8

from django.conf.urls.defaults import patterns, include

from dext.views import resource_patterns

from the_tale.bank.xsolla.views import XsollaResource

urlpatterns = patterns('',
                       (r'^', include(resource_patterns(XsollaResource))),
)
