
import smart_imports

smart_imports.all()


urlpatterns = [django_urls.url(r'^tokens/', django_urls.include(dext_old_views.resource_patterns(views.TokensResource), namespace='tokens'))]
