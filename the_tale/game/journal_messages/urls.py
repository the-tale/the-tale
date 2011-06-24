from django_next.views.dispatcher import resource_patterns

from .views import JournalMessagesResource

urlpatterns = resource_patterns(JournalMessagesResource)
