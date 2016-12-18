# coding: utf-8

from dext.views import resource_patterns

from the_tale.accounts.friends.views import FriendsResource

urlpatterns = resource_patterns(FriendsResource)
