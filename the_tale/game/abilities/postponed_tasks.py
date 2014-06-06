# coding: utf-8

from the_tale.game.abilities.relations import ABILITY_TYPE

from the_tale.game.postponed_tasks import ComplexChangeTask



class UseAbilityTask(ComplexChangeTask):
    TYPE = 'user-ability'

    def construct_processor(self):
        from the_tale.game.abilities.deck import ABILITIES
        return ABILITIES[ABILITY_TYPE(self.processor_id)]()
