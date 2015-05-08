# coding: utf-8

from django.conf.urls import patterns, include

urlpatterns = patterns('',
                       (r'^xsolla/', include('the_tale.finances.xsolla.urls', namespace='xsolla') )
                      )
