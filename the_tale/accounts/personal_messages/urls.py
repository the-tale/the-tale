# coding: utf-8

from dext.views.dispatcher import resource_patterns

from accounts.personal_messages.views import MessageResource

urlpatterns = resource_patterns(MessageResource)
