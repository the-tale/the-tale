# coding: utf-8

from the_tale.game.cards import relations

from the_tale.game.postponed_tasks import ComplexChangeTask



class UseCardTask(ComplexChangeTask):
    TYPE = 'use-card'

    def construct_processor(self):
        from the_tale.game.cards.prototypes import CARDS
        return CARDS[relations.CARD_TYPE(self.processor_id)]()
