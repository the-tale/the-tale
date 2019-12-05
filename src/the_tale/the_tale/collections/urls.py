
import smart_imports

smart_imports.all()


urlpatterns = [django_urls.url(r'^kits/', django_urls.include((old_views.resource_patterns(views.KitsResource), 'kits'))),
               django_urls.url(r'^collections/', django_urls.include((old_views.resource_patterns(views.CollectionsResource), 'collections'))),
               django_urls.url(r'^items/', django_urls.include((old_views.resource_patterns(views.ItemsResource), 'items')))]
