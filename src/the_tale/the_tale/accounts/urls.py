# coding: utf-8

from django.conf.urls import url
from django.conf.urls import include

from dext.views import resource_patterns

from the_tale.accounts import views

urlpatterns = [url(r'^registration/', include(resource_patterns(views.RegistrationResource), namespace='registration')),
               url(r'^profile/', include(resource_patterns(views.ProfileResource), namespace='profile')),
               url(r'^auth/', include(resource_patterns(views.AuthResource), namespace='auth')),
               url(r'^messages/', include('the_tale.accounts.personal_messages.urls', namespace='messages') ),
               url(r'^friends/', include('the_tale.accounts.friends.urls', namespace='friends')),
               url(r'^clans/', include('the_tale.accounts.clans.urls', namespace='clans')),
               url(r'^achievements/', include('the_tale.accounts.achievements.urls', namespace='achievements')),
               url(r'^third-party/', include('the_tale.accounts.third_party.urls', namespace='third-party')),
               url(r'^', include(views.accounts_resource.get_urls()))]
