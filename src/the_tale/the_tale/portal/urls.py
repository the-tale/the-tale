
import smart_imports

smart_imports.all()


urlpatterns = [django_urls.url(r'^developers-info/', django_urls.include('the_tale.portal.developers_info.urls', namespace='developers-info'))]

urlpatterns += dext_old_views.resource_patterns(views.PortalResource)
