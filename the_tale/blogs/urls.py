# coding: utf-8

from django.conf.urls import patterns, include

from dext.views import resource_patterns

from the_tale.blogs.views import PostResource

urlpatterns = patterns('',
                       (r'^posts/', include(resource_patterns(PostResource), namespace='posts')),
)
