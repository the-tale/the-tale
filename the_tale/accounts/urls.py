# coding: utf-8

from django.conf.urls.defaults import patterns, include

from dext.views.dispatcher import resource_patterns

from accounts.views import RegistrationResource, ProfileResource, AuthResource, AccountResource

urlpatterns = patterns('',
                       (r'^registration/', include(resource_patterns(RegistrationResource), namespace='registration')),
                       (r'^profile/', include(resource_patterns(ProfileResource), namespace='profile')),
                       (r'^auth/', include(resource_patterns(AuthResource), namespace='auth')),
                       (r'^', include(resource_patterns(AccountResource))),
)
