from django_next.views.dispatcher import resource_patterns

from .views import PlaceResource

urlpatterns = resource_patterns(PlaceResource)
