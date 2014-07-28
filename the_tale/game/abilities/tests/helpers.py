# coding: utf-8

from the_tale.game.tests.helpers import ComplexChangeTaskMixin

from the_tale.game.abilities.postponed_tasks import UseAbilityTask



class UseAbilityTaskMixin(ComplexChangeTaskMixin):
    LOGIC = UseAbilityTask

    # @property
    # def PROCESSOR(self): return self.ABILITY.TYPE
