
import smart_imports

smart_imports.all()

               # wrong names url, leaved to allow old links worked correctly
urlpatterns = [django_urls.url('^folclor/(?P<path>.*)$', RedirectView.as_view(url='/folklore/%(path)s')),
               django_urls.url('^accounts/clans/(?P<path>.*)$', RedirectView.as_view(url='/clans/%(path)s')),

               django_urls.url(r'^admin/', django_urls.include(django_admin.site.urls)),
               django_urls.url(r'^accounts/', django_urls.include('the_tale.accounts.urls', namespace='accounts')),
               django_urls.url(r'^clans/', django_urls.include('the_tale.clans.urls', namespace='clans')),
               django_urls.url(r'^game/', django_urls.include('the_tale.game.urls', namespace='game')),
               django_urls.url(r'^guide/', django_urls.include('the_tale.guide.urls', namespace='guide')),
               django_urls.url(r'^forum/', django_urls.include('the_tale.forum.urls', namespace='forum')),

               django_urls.url(r'^folklore/', django_urls.include('the_tale.blogs.urls', namespace='blogs')),
               django_urls.url(r'^collections/', django_urls.include('the_tale.collections.urls', namespace='collections')),
               django_urls.url(r'^news/', django_urls.include('the_tale.news.urls', namespace='news')),
               django_urls.url(r'^postponed-tasks/', django_urls.include('the_tale.common.postponed_tasks.urls', namespace='postponed-tasks')),
               django_urls.url(r'^bank/', django_urls.include('the_tale.finances.bank.urls', namespace='bank')),
               django_urls.url(r'^shop/', django_urls.include('the_tale.finances.shop.urls', namespace='shop')),
               django_urls.url(r'^statistics/', django_urls.include('the_tale.statistics.urls', namespace='statistics')),
               django_urls.url(r'^linguistics/', django_urls.include('the_tale.linguistics.urls', namespace='linguistics')),
               django_urls.url(r'^', django_urls.include('the_tale.portal.urls', namespace='portal'))]


if django_settings.DEBUG:
    urlpatterns += django_static.static(django_settings.STATIC_URL + 'admin/', document_root=os.path.join(os.path.dirname(django_admin.__file__), 'static', 'admin'))
    urlpatterns += [django_urls.url(r'^{}css/'.format(django_settings.STATIC_URL[1:]), django_urls.include('the_tale.common.less.urls'))]
    urlpatterns += django_static.static(django_settings.STATIC_URL, document_root=os.path.join(django_settings.PROJECT_DIR, 'static'))


handlerCSRF = old_views.create_handler_view(portal_views.PortalResource, 'handlerCSRF')
handler403 = old_views.create_handler_view(portal_views.PortalResource, 'handler403')
handler404 = old_views.create_handler_view(portal_views.PortalResource, 'handler404')
handler500 = old_views.create_handler_view(portal_views.PortalResource, 'handler500')
