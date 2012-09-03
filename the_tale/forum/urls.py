# coding: utf-8

from django.conf.urls.defaults import patterns, include

from dext.views.dispatcher import resource_patterns

from forum.views import ForumResource, PostsResource, ThreadsResource

urlpatterns = patterns('',
                       (r'^posts/', include(resource_patterns(PostsResource), namespace='posts')),
                       (r'^threads/', include(resource_patterns(ThreadsResource), namespace='threads')),
                       (r'^', include(resource_patterns(ForumResource)) )
)
