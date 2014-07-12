# coding: utf-8

from dext.views import resource_patterns
from the_tale.game.quests.views import QuestsResource

urlpatterns = resource_patterns(QuestsResource)
