
import smart_imports

smart_imports.all()


urlpatterns = [django_urls.url(r'^', django_urls.include(dext_old_views.resource_patterns(views.XsollaResource))), ]
