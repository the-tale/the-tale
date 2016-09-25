# coding: utf-8

from django.conf.urls import patterns, include

from dext.views import resource_patterns

from the_tale.finances.xsolla.views import XsollaResource

urlpatterns = patterns('',
                       (r'^', include(resource_patterns(XsollaResource))),
)
