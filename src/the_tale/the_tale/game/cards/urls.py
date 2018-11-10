
import smart_imports

smart_imports.all()


urlpatterns = views.resource.get_urls() + views.technical_resource.get_urls()
