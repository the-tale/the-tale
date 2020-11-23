
import smart_imports

smart_imports.all()


urlpatterns = [django_urls.url(r'^xsolla/', django_urls.include(('the_tale.finances.xsolla.urls', 'xsolla')))]

urlpatterns += views.technical_resource.get_urls()
