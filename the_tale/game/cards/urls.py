from django_next.views.dispatcher import resource_patterns

from .views import CardsResource

urlpatterns = resource_patterns(CardsResource)
