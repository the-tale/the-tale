#coding: utf-8

from game.heroes.habilities.prototypes import AbilityPrototype, ABILITY_TYPE, ABILITIES_ACTIVATION_TYPE



class CHARISMA(AbilityPrototype):

    TYPE = ABILITY_TYPE.STATIC
    ACTIVATION_TYPE = ABILITIES_ACTIVATION_TYPE.PASSIVE

    NAME = u'Харизматичность'
    normalized_name = NAME
    DESCRIPTION = u'Герой настолько обоятелен, что умудряется получать лучшие награды за выполнение заданий.'

    MONEY_MULTIPLIER = 3

    @classmethod
    def update_quest_reward(cls, hero, money):
        return int(money * cls.MONEY_MULTIPLIER)


ABILITIES = dict( (ability.get_id(), ability)
                  for ability in globals().values()
                  if isinstance(ability, type) and issubclass(ability, AbilityPrototype) and ability != AbilityPrototype)
