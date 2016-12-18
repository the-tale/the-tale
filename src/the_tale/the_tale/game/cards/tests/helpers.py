# coding: utf-8

from the_tale.game.tests.helpers import ComplexChangeTaskMixin

from the_tale.game.cards.postponed_tasks import UseCardTask



class CardsTestMixin(ComplexChangeTaskMixin):
    LOGIC = UseCardTask
