
import smart_imports

smart_imports.all()

               # wrong names url, leaved to allow old links worked correctly
urlpatterns = [django_urls.url('^folclor/(?P<path>.*)$', RedirectView.as_view(url='/folklore/%(path)s')),
               django_urls.url('^accounts/clans/(?P<path>.*)$', RedirectView.as_view(url='/clans/%(path)s')),

               django_urls.url(r'^admin/', django_admin.site.urls),
               django_urls.url(r'^accounts/', django_urls.include(('the_tale.accounts.urls', 'accounts'))),
               django_urls.url(r'^clans/', django_urls.include(('the_tale.clans.urls', 'clans'))),
               django_urls.url(r'^game/', django_urls.include(('the_tale.game.urls', 'game'))),
               django_urls.url(r'^guide/', django_urls.include(('the_tale.guide.urls', 'guide'))),
               django_urls.url(r'^forum/', django_urls.include(('the_tale.forum.urls', 'forum'))),

               django_urls.url(r'^folklore/', django_urls.include(('the_tale.blogs.urls', 'blogs'))),
               django_urls.url(r'^collections/', django_urls.include(('the_tale.collections.urls', 'collections'))),
               django_urls.url(r'^news/', django_urls.include(('the_tale.news.urls', 'news'))),
               django_urls.url(r'^postponed-tasks/', django_urls.include(('the_tale.common.postponed_tasks.urls', 'postponed-tasks'))),
               django_urls.url(r'^bank/', django_urls.include(('the_tale.finances.bank.urls', 'bank'))),
               django_urls.url(r'^shop/', django_urls.include(('the_tale.finances.shop.urls', 'shop'))),
               django_urls.url(r'^statistics/', django_urls.include(('the_tale.statistics.urls', 'statistics'))),
               django_urls.url(r'^linguistics/', django_urls.include(('the_tale.linguistics.urls', 'linguistics'))),
               django_urls.url(r'^', django_urls.include(('the_tale.portal.urls', 'portal')))]


if django_settings.DEBUG:
    urlpatterns += django_static.static(django_settings.STATIC_URL + 'admin/',
                                        document_root=os.path.join(os.path.dirname(django_admin.__file__), 'static', 'admin'))
    urlpatterns += [django_urls.url(r'^{}css/'.format(django_settings.STATIC_URL[1:]), django_urls.include('the_tale.common.less.urls'))]
    urlpatterns += django_static.static(django_settings.STATIC_URL, document_root=os.path.join(django_settings.PROJECT_DIR, 'static'))


handlerCSRF = old_views.create_handler_view(portal_views.PortalResource, 'handlerCSRF')
handler403 = old_views.create_handler_view(portal_views.PortalResource, 'handler403')
handler404 = old_views.create_handler_view(portal_views.PortalResource, 'handler404')
handler500 = old_views.create_handler_view(portal_views.PortalResource, 'handler500')
