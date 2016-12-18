# coding: utf-8

from django.conf.urls import url
from django.conf.urls import include

from dext.views import resource_patterns

from the_tale.finances.xsolla.views import XsollaResource

urlpatterns = [url(r'^', include(resource_patterns(XsollaResource))),]
