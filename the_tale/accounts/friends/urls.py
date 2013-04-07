# coding: utf-8

from dext.views import resource_patterns

from accounts.friends.views import FriendsResource

urlpatterns = resource_patterns(FriendsResource)
