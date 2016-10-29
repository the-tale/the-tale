# coding: utf-8

import os

from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin
from django.conf import settings as project_settings
from django.views.generic.base import RedirectView

from dext.views import create_handler_view

from the_tale.portal.views import PortalResource # pylint: disable=W0403

urlpatterns = [url(r'^', include('the_tale.cms.urls', namespace='cms') ),
               url(r'^admin/', include(admin.site.urls)),
               url(r'^accounts/', include('the_tale.accounts.urls', namespace='accounts') ),
               url(r'^game/', include('the_tale.game.urls', namespace='game') ),
               url(r'^guide/', include('the_tale.guide.urls', namespace='guide') ),
               url(r'^forum/', include('the_tale.forum.urls', namespace='forum') ),

               url('^folclor/(?P<path>.*)$', RedirectView.as_view(url='/folklore/%(path)s')), # wrong names url, leaved to allow old links worked correctly

               url(r'^folklore/', include('the_tale.blogs.urls', namespace='blogs') ),
               url(r'^collections/', include('the_tale.collections.urls', namespace='collections') ),
               url(r'^news/', include('the_tale.cms.news.urls', namespace='news') ),
               url(r'^postponed-tasks/', include('the_tale.common.postponed_tasks.urls', namespace='postponed-tasks') ),
               url(r'^market/', include('the_tale.finances.market.urls', namespace='market') ),
               url(r'^bank/', include('the_tale.finances.bank.urls', namespace='bank') ),
               url(r'^shop/', include('the_tale.finances.shop.urls', namespace='shop')),
               url(r'^statistics/', include('the_tale.statistics.urls', namespace='statistics') ),
               url(r'^linguistics/', include('the_tale.linguistics.urls', namespace='linguistics') ),
               url(r'^', include('the_tale.portal.urls', namespace='portal') ) ]


if project_settings.DEBUG:
    urlpatterns += static(project_settings.ADMIN_DEBUG_MEDIA_PREFIX, document_root=os.path.join(os.path.dirname(admin.__file__), 'static', 'admin'))
    urlpatterns += [url(r'^%scss/' % project_settings.STATIC_DEBUG_URL[1:], include('dext.less.urls') )]
    urlpatterns += static(project_settings.STATIC_DEBUG_URL, document_root=project_settings.STATIC_DIR)


handlerCSRF = create_handler_view(PortalResource, 'handlerCSRF')
handler403 = create_handler_view(PortalResource, 'handler403')
handler404 = create_handler_view(PortalResource, 'handler404')
handler500 = create_handler_view(PortalResource, 'handler500')

# import resource
# import gc
# gc.collect()
# print('memory usage: {}'.format(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024))
