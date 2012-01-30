# coding: utf-8
from ...heroes.hmessages import generator as msg_generator

from ..prototypes import AbilityPrototype

attrs = None

class HealHero(AbilityPrototype):

    LIMITED = False
    INITIAL_LIMIT = None

    COST = 10
    COOLDOWN = 25

    NAME = u'Вылечить'
    DESCRIPTION = u'Попытаться немного подлечить героя'
    ARTISTIC = u'К ужасу противников раны на теле героя начали затягиваться и через несколько мгновений тот, перехватив оружие, с новыми силами ринулся в бой.'

    FORM = None
    TEMPLATE = None
      
    def use(self, bundle, angel, hero, form):
        old_health = hero.health
        hero.health = min(hero.max_health, hero.health + hero.max_health * 0.3)
        hero.push_message(msg_generator.msg_ability_healhero_activate(hero, hero.health - old_health))
        return True


