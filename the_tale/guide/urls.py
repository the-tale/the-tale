# coding: utf-8
from django.conf.urls import patterns, include

from dext.views import resource_patterns

from the_tale.game.mobs.views import GuideMobResource
from the_tale.game.artifacts.views import GuideArtifactResource
from the_tale.game.cards import views as cards_views
from the_tale.game.companions.views import resource as companions_resource

from the_tale.guide.views import GuideResource


urlpatterns = resource_patterns(GuideResource)

urlpatterns += patterns('',
                       (r'^mobs/', include(resource_patterns(GuideMobResource), namespace='mobs') ),
                       (r'^artifacts/', include(resource_patterns(GuideArtifactResource), namespace='artifacts') ),
                       (r'^cards/', include(cards_views.guide_resource.get_urls(), namespace='cards') ),
                       (r'^companions/', include(companions_resource.get_urls(), namespace='companions') )
    )
