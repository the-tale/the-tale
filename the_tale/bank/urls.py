# coding: utf-8

from django.conf.urls import patterns, include

urlpatterns = patterns('',
                       (r'^xsolla/', include('the_tale.bank.xsolla.urls', namespace='xsolla') )
)
