# coding: utf-8

from ...heroes.hmessages import generator as msg_generator
from ...actions.prototypes import ActionBattlePvE_1x1Prototype

from ..prototypes import AbilityPrototype

attrs = None

class Lightning(AbilityPrototype):

    LIMITED = False
    INITIAL_LIMIT = None

    COST = 10
    COOLDOWN = 10

    NAME = u'Жахнуть'
    DESCRIPTION = u'Применить свою англельскую силу и покарать супостатов'
    ARTISTIC = u'Из искры да разгорится пламя'

    FORM = None
    TEMPLATE = None
      
    def use(self, bundle, angel, hero, form):
        battle_action = bundle.current_hero_action(hero.id)

        if battle_action.type != ActionBattlePvE_1x1Prototype.TYPE:
            return False

        if not battle_action.bit_mob(0.3):
            return False

        hero.push_message(msg_generator.msg_ability_lightning_activate(hero, battle_action.mob))

        return True

