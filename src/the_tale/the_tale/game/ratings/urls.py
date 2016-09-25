# coding: utf-8

from dext.views import resource_patterns

from the_tale.game.ratings.views import RatingResource

urlpatterns = resource_patterns(RatingResource)
