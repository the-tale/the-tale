from django.conf.urls.defaults import patterns, url, include

from django.contrib import admin

from django_next import jinja2 as jinja2_next
from django_next.views.views import template_renderer

admin.autodiscover()
jinja2_next.autodiscover()

urlpatterns = patterns('',
                       url(r'^less/', include('django_next.less.urls') ), #TODO: replace with settings.LESS_URL
                       (r'^admin/', include(admin.site.urls)),
                       url(r'^$', template_renderer('index.html'), name='index'),
                       (r'^accounts/', include('accounts.urls', namespace='accounts') ),
                       (r'^game/', include('game.urls', namespace='game') ),
)
