# coding: utf-8

from ..prototypes import AbilityPrototype

attrs = None

class HealHero(AbilityPrototype):

    LIMITED = False
    INITIAL_LIMIT = None

    COST = 30
    COOLDOWN = 10

    NAME = u'Вылечить'
    DESCRIPTION = u'Попытаться немного подлечить героя'
    ARTISTIC = u'К ужасу противников раны на теле героя начали затягиваться и через несколько мгновений тот, перехватив оружие, с новыми силами ринулся в бой.'

    FORM = None
    TEMPLATE = None
      
    def use(self, bundle, angel, hero, form):
        old_health = hero.health
        hero.health = min(hero.max_health, hero.health + hero.max_health * 0.3)
        hero.add_message('angel_ability_healhero', hero=hero, health=(hero.health-old_health))
        return True


