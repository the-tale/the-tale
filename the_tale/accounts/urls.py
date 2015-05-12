# coding: utf-8

from django.conf.urls import patterns, include

from dext.views import resource_patterns

from the_tale.accounts import views

urlpatterns = patterns('',
                       (r'^registration/', include(resource_patterns(views.RegistrationResource), namespace='registration')),
                       (r'^profile/', include(resource_patterns(views.ProfileResource), namespace='profile')),
                       (r'^auth/', include(resource_patterns(views.AuthResource), namespace='auth')),
                       (r'^messages/', include('the_tale.accounts.personal_messages.urls', namespace='messages') ),
                       (r'^friends/', include('the_tale.accounts.friends.urls', namespace='friends')),
                       (r'^clans/', include('the_tale.accounts.clans.urls', namespace='clans')),
                       (r'^achievements/', include('the_tale.accounts.achievements.urls', namespace='achievements')),
                       (r'^third-party/', include('the_tale.accounts.third_party.urls', namespace='third-party')),
                       (r'^', include(views.accounts_resource.get_urls())),
                      )
