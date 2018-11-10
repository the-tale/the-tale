
import smart_imports

smart_imports.all()


urlpatterns = [django_urls.url(r'^words/', django_urls.include(dext_old_views.resource_patterns(views.WordResource), namespace='words')),
               django_urls.url(r'^templates/', django_urls.include(dext_old_views.resource_patterns(views.TemplateResource), namespace='templates'))]


urlpatterns += dext_old_views.resource_patterns(views.LinguisticsResource)
