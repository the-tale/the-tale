
import smart_imports

smart_imports.all()


urlpatterns = [django_urls.url(r'^(?P<path>.*).css$', views.less_compiler)]
