# coding: utf-8

from django.conf.urls.defaults import patterns, include

urlpatterns = patterns('',
                       (r'^dengionline/', include('the_tale.bank.dengionline.urls', namespace='dengionline') ),
                       (r'^xsolla/', include('the_tale.bank.xsolla.urls', namespace='xsolla') )
)
