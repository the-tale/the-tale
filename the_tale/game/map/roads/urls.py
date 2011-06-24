from django_next.views.dispatcher import resource_patterns

from .views import RoadsResource

urlpatterns = resource_patterns(RoadsResource)
