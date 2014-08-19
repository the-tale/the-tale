# coding: utf-8

from dext.views import resource_patterns

from the_tale.game.phrase_candidates import views


urlpatterns = resource_patterns(views.PhraseCandidateResource)
