# coding: utf-8

import os

from django.conf.urls import patterns, url, include
from django.conf.urls.static import static
from django.contrib import admin
from django.conf import settings as project_settings
from django.views.generic.base import RedirectView

from dext import jinja2 as jinja2_next
from dext.views import create_handler_view

from the_tale.portal.views import PortalResource # pylint: disable=W0403

from the_tale.common import postponed_tasks # pylint: disable=W0403

from the_tale.market import goods_types

jinja2_next.autodiscover()


urlpatterns = patterns('',
                       (r'^', include('the_tale.cms.urls', namespace='cms') ),
                       (r'^admin/', include(admin.site.urls)),
                       (r'^accounts/', include('the_tale.accounts.urls', namespace='accounts') ),
                       (r'^game/', include('the_tale.game.urls', namespace='game') ),
                       (r'^guide/', include('the_tale.guide.urls', namespace='guide') ),
                       (r'^forum/', include('the_tale.forum.urls', namespace='forum') ),

                       ('^folclor/(?P<path>.*)$', RedirectView.as_view(url='/folklore/%(path)s')), # wrong names url, leaved to allow old links worked correctly

                       (r'^folklore/', include('the_tale.blogs.urls', namespace='blogs') ),
                       (r'^collections/', include('the_tale.collections.urls', namespace='collections') ),
                       (r'^news/', include('the_tale.cms.news.urls', namespace='news') ),
                       (r'^postponed-tasks/', include('the_tale.common.postponed_tasks.urls', namespace='postponed-tasks') ),
                       (r'^market/', include('the_tale.market.urls', namespace='market') ),
                       (r'^bank/', include('the_tale.bank.urls', namespace='bank') ),
                       (r'^statistics/', include('the_tale.statistics.urls', namespace='statistics') ),
                       (r'^linguistics/', include('the_tale.linguistics.urls', namespace='linguistics') ),
                       (r'^', include('the_tale.portal.urls', namespace='portal') ),
)


if project_settings.DEBUG:
    urlpatterns += static(project_settings.ADMIN_DEBUG_MEDIA_PREFIX, document_root=os.path.join(os.path.dirname(admin.__file__), 'static', 'admin'))
    urlpatterns += patterns('',
                            url(r'^%scss/' % project_settings.STATIC_DEBUG_URL[1:], include('dext.less.urls') )
                            )
    urlpatterns += static(project_settings.DCONT_DEBUG_URL, document_root=project_settings.DCONT_DIR)
    urlpatterns += static(project_settings.STATIC_DEBUG_URL, document_root=project_settings.STATIC_DIR)


handlerCSRF = create_handler_view(PortalResource, 'handlerCSRF')
handler403 = create_handler_view(PortalResource, 'handler403')
handler404 = create_handler_view(PortalResource, 'handler404')
handler500 = create_handler_view(PortalResource, 'handler500')
