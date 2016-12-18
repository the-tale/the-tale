# coding: utf-8

from django.conf.urls import url
from django.conf.urls import include

from dext.views import resource_patterns

from the_tale.collections.views import KitsResource, CollectionsResource, ItemsResource

urlpatterns = [url(r'^kits/', include(resource_patterns(KitsResource), namespace='kits')),
               url(r'^collections/', include(resource_patterns(CollectionsResource), namespace='collections')),
               url(r'^items/', include(resource_patterns(ItemsResource), namespace='items'))]
