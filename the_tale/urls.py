# coding: utf-8

import os

from django.conf.urls.defaults import patterns, url, include
from django.conf.urls.static import static
from django.contrib import admin
from django.conf import settings as project_settings

from dext import jinja2 as jinja2_next
from dext.views import create_handler_view

from portal.views import PortalResource # pylint: disable=W0403

from common import postponed_tasks # pylint: disable=W0403

admin.autodiscover()
jinja2_next.autodiscover()
postponed_tasks.autodiscover()

urlpatterns = patterns('',
                       (r'^', include('cms.urls', namespace='cms') ),
                       (r'^admin/', include(admin.site.urls)),
                       (r'^accounts/', include('accounts.urls', namespace='accounts') ),
                       (r'^game/', include('game.urls', namespace='game') ),
                       (r'^guide/', include('guide.urls', namespace='guide') ),
                       (r'^forum/', include('forum.urls', namespace='forum') ),
                       (r'^folclor/', include('blogs.urls', namespace='blogs') ),
                       (r'^news/', include('cms.news.urls', namespace='news') ),
                       (r'^postponed-tasks/', include('common.postponed_tasks.urls', namespace='postponed-tasks') ),
                       (r'^bank/', include('bank.urls', namespace='bank') ),
                       (r'^', include('portal.urls', namespace='portal') ),
)


if project_settings.DEBUG:
    urlpatterns += static(project_settings.ADMIN_MEDIA_PREFIX, document_root=os.path.join(os.path.dirname(admin.__file__), 'static', 'admin'))
    urlpatterns += patterns('',
                            url(r'^%scss/' % project_settings.STATIC_URL[1:], include('dext.less.urls') )
                            )
    urlpatterns += static(project_settings.DCONT_URL, document_root=project_settings.DCONT_DIR)
    urlpatterns += static(project_settings.STATIC_URL, document_root=project_settings.STATIC_DIR)


handler404 = create_handler_view(PortalResource, 'handler404')
handler500 = create_handler_view(PortalResource, 'handler500')
