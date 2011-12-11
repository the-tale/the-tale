# coding: utf-8

from ..prototypes import AbilityPrototype

attrs = None

class HealHero(AbilityPrototype):

    LIMITED = False
    INITIAL_LIMIT = None

    COST = 10
    COOLDOWN = 10

    NAME = u'Вылечить'
    DESCRIPTION = u'Попытаться немного подлечить героя'
    ARTISTIC = u'К ужасу противников раны на теле героя начали затягиваться и через несколько мгновений тот, перехватив оружие, с новыми силами ринулся в бой.'

    FORM = None
    TEMPLATE = None
      
    def use(self, angel, hero, form):
        old_health = hero.health
        hero.health = min(hero.max_health, hero.health + hero.max_health * 0.1)
        hero.create_tmp_log_message('You heal hero for %d HP' % (hero.health - old_health))


