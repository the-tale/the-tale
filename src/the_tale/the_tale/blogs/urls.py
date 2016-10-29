# coding: utf-8

from django.conf.urls import url
from django.conf.urls import include

from dext.views import resource_patterns

from the_tale.blogs.views import PostResource

urlpatterns = [url(r'^posts/', include(resource_patterns(PostResource), namespace='posts')),]
