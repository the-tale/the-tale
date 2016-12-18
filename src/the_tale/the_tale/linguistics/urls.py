# coding: utf-8

from django.conf.urls import url
from django.conf.urls import include

from dext.views import resource_patterns

from the_tale.linguistics import views


urlpatterns = [url(r'^words/', include(resource_patterns(views.WordResource), namespace='words') ),
               url(r'^templates/', include(resource_patterns(views.TemplateResource), namespace='templates') ) ]


urlpatterns += resource_patterns(views.LinguisticsResource)
