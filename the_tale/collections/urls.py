# coding: utf-8

from django.conf.urls import patterns, include

from dext.views import resource_patterns

from the_tale.collections.views import KitsResource, CollectionsResource, ItemsResource

urlpatterns = patterns('',
                       (r'^kits/', include(resource_patterns(KitsResource), namespace='kits')),
                       (r'^collections/', include(resource_patterns(CollectionsResource), namespace='collections')),
                       (r'^items/', include(resource_patterns(ItemsResource), namespace='items'))
)
