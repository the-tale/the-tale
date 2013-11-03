# coding: utf-8

from dext.views import resource_patterns

from the_tale.accounts.personal_messages.views import MessageResource

urlpatterns = resource_patterns(MessageResource)
