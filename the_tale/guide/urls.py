# coding: utf-8
from django.conf.urls.defaults import patterns, include

from dext.views import resource_patterns

from game.mobs.views import GuideMobResource
from game.artifacts.views import GuideArtifactResource

from guide.views import GuideResource

urlpatterns = resource_patterns(GuideResource)

urlpatterns += patterns('',
                       (r'^mobs/', include(resource_patterns(GuideMobResource), namespace='mobs') ),
                       (r'^artifacts/', include(resource_patterns(GuideArtifactResource), namespace='artifacts') )
    )
