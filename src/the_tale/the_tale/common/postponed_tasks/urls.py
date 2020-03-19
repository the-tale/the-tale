
import smart_imports

smart_imports.all()


urlpatterns = old_views.resource_patterns(views.PostponedTaskResource)
