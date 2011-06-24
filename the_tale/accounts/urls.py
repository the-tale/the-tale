
from django_next.views.dispatcher import resource_patterns

from .views import AccountsResource

urlpatterns = resource_patterns(AccountsResource)











