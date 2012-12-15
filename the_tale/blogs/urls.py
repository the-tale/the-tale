# coding: utf-8

from django.conf.urls.defaults import patterns, include

from dext.views.dispatcher import resource_patterns

from blogs.views import PostResource

urlpatterns = patterns('',
                       (r'^posts/', include(resource_patterns(PostResource), namespace='posts')),
)
