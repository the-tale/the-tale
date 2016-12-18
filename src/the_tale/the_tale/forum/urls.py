# coding: utf-8

from django.conf.urls import url
from django.conf.urls import include

from dext.views import resource_patterns

from the_tale.forum.views import ForumResource, PostsResource, ThreadsResource, SubscriptionsResource, SubCategoryResource

urlpatterns = [url(r'^posts/', include(resource_patterns(PostsResource), namespace='posts')),
               url(r'^threads/', include(resource_patterns(ThreadsResource), namespace='threads')),
               url(r'^subcategories/', include(resource_patterns(SubCategoryResource), namespace='subcategories')),
               url(r'^subscriptions/', include(resource_patterns(SubscriptionsResource), namespace='subscriptions')),
               url(r'^', include(resource_patterns(ForumResource)) )]
