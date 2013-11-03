# coding: utf-8

from django.conf.urls.defaults import patterns, include

from dext.views import resource_patterns

from achievements.views import KitsResource, SectionsResource, RewardsResource, AccountsResource

urlpatterns = patterns('',
                       (r'^kits/', include(resource_patterns(KitsResource), namespace='kits')),
                       (r'^sections/', include(resource_patterns(SectionsResource), namespace='sections')),
                       (r'^achievements/', include(resource_patterns(RewardsResource), namespace='rewards')),
                       (r'^', include(resource_patterns(AccountsResource)) )
)
