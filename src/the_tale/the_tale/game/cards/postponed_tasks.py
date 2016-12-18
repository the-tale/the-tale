# coding: utf-8

from the_tale.game.cards import relations

from the_tale.game.postponed_tasks import ComplexChangeTask



class UseCardTask(ComplexChangeTask):
    TYPE = 'use-card'

    def construct_processor(self):
        from the_tale.game.cards import effects
        return effects.EFFECTS[relations.CARD_TYPE(self.processor_id)]
