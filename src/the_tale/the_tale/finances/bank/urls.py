# coding: utf-8

from django.conf.urls import url
from django.conf.urls import include

urlpatterns = [url(r'^xsolla/', include('the_tale.finances.xsolla.urls', namespace='xsolla') )]
