# coding: utf-8

from django.conf.urls import patterns, include

from the_tale.game.map import views


urlpatterns = patterns('',
                       (r'^places/', include('the_tale.game.map.places.urls', namespace='places') ),
                      )


urlpatterns += views.resource.get_urls()
