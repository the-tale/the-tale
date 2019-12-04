
import smart_imports

smart_imports.all()


urlpatterns = [django_urls.url(r'^words/', django_urls.include(old_views.resource_patterns(views.WordResource), namespace='words')),
               django_urls.url(r'^templates/', django_urls.include(old_views.resource_patterns(views.TemplateResource), namespace='templates'))]


urlpatterns += old_views.resource_patterns(views.LinguisticsResource)
