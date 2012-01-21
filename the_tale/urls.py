from django.conf.urls.defaults import patterns, url, include

from django.contrib import admin
from django.conf import settings as project_settings

from django_next import jinja2 as jinja2_next
from django_next.views.views import template_renderer
from django_next.views.dispatcher import create_handler_view

from portal.views import PortalResource

admin.autodiscover()
jinja2_next.autodiscover()

urlpatterns = patterns('',
                       (r'^admin/', include(admin.site.urls)),
                       (r'^accounts/', include('accounts.urls', namespace='accounts') ),
                       (r'^game/', include('game.urls', namespace='game') ),
                       (r'^', include('portal.urls', namespace='portal') ),
)

if project_settings.DEBUG:
    urlpatterns += patterns('', 
                            url(r'^tmp/?$', template_renderer('tmp.html'), name='tmp'),
                            url(r'^less/', include('django_next.less.urls') ) #TODO: replace with settings.LESS_URL)
                            )

handler404 = create_handler_view(PortalResource, 'handler404')
handler500 = create_handler_view(PortalResource, 'handler500')
