# coding: utf-8

from dext.views.dispatcher import resource_patterns

from game.ratings.views import RatingResource

urlpatterns = resource_patterns(RatingResource)
