# coding: utf-8

from the_tale.game.cards import cards

from the_tale.game.postponed_tasks import ComplexChangeTask



class UseCardTask(ComplexChangeTask):
    TYPE = 'use-card'

    def construct_processor(self):
        return cards.CARD(self.processor_id).effect
