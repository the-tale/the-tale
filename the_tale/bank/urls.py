# coding: utf-8

from django.conf.urls.defaults import patterns, include

urlpatterns = patterns('',
                       (r'^dengionline/', include('bank.dengionline.urls', namespace='dengionline') )
)
