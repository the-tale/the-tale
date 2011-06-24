from django_next.views.dispatcher import resource_patterns

from .views import TurnsResource

urlpatterns = resource_patterns(TurnsResource)
