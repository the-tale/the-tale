#coding: utf-8

from game.heroes.habilities.prototypes import AbilityPrototype, ABILITY_TYPE, ABILITIES_ACTIVATION_TYPE



class CHARISMA(AbilityPrototype):

    TYPE = ABILITY_TYPE.NONBATTLE
    ACTIVATION_TYPE = ABILITIES_ACTIVATION_TYPE.PASSIVE

    NAME = u'Харизматичный'
    normalized_name = NAME
    DESCRIPTION = u'Герой настолько обоятелен, что умудряется получать лучшие награды за выполнение заданий.'

    MONEY_MULTIPLIER = 3

    @classmethod
    def update_quest_reward(cls, hero, money):
        return int(money * cls.MONEY_MULTIPLIER)


class HUCKSTER(AbilityPrototype):

    TYPE = ABILITY_TYPE.NONBATTLE
    ACTIVATION_TYPE = ABILITIES_ACTIVATION_TYPE.PASSIVE

    NAME = u'Торгаш'
    normalized_name = NAME
    DESCRIPTION = u'Увеличивается цена продажи и уменьшается цена покупки предметов.'

    SELL_MULTIPLIER = 1.2
    BUY_MULTIPLIER = 0.8

    @classmethod
    def update_buy_price(cls, hero, money):
        return int(money * cls.BUY_MULTIPLIER)

    @classmethod
    def update_sell_price(cls, hero, money):
        ''' +1 for increase price on low levels'''
        return int(money * cls.SELL_MULTIPLIER + 1)


ABILITIES = dict( (ability.get_id(), ability)
                  for ability in globals().values()
                  if isinstance(ability, type) and issubclass(ability, AbilityPrototype) and ability != AbilityPrototype)
