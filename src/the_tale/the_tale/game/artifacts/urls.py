# coding: utf-8

from dext.views import resource_patterns

from the_tale.game.artifacts.views import GameArtifactResource

urlpatterns = resource_patterns(GameArtifactResource)
