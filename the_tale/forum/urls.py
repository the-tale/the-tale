# coding: utf-8

from django.conf.urls.defaults import patterns, include

from dext.views import resource_patterns

from forum.views import ForumResource, PostsResource, ThreadsResource, SubscriptionsResource, SubCategoryResource

urlpatterns = patterns('',
                       (r'^posts/', include(resource_patterns(PostsResource), namespace='posts')),
                       (r'^threads/', include(resource_patterns(ThreadsResource), namespace='threads')),
                       (r'^subcategories/', include(resource_patterns(SubCategoryResource), namespace='subcategories')),
                       (r'^subscriptions/', include(resource_patterns(SubscriptionsResource), namespace='subscriptions')),
                       (r'^', include(resource_patterns(ForumResource)) )
)
