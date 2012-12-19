#coding: utf-8

from game.heroes.habilities.prototypes import AbilityPrototype, ABILITY_TYPE, ABILITY_ACTIVATION_TYPE, ABILITY_AVAILABILITY


class CHARISMA(AbilityPrototype):

    TYPE = ABILITY_TYPE.NONBATTLE
    ACTIVATION_TYPE = ABILITY_ACTIVATION_TYPE.PASSIVE
    AVAILABILITY = ABILITY_AVAILABILITY.FOR_PLAYERS

    NAME = u'Харизматичный'
    normalized_name = NAME
    DESCRIPTION = u'Герой настолько обаятелен, что умудряется получать лучшие награды за выполнение заданий.'

    MONEY_MULTIPLIER = 3

    def update_quest_reward(self, hero, money):
        return int(money * self.MONEY_MULTIPLIER)


class HUCKSTER(AbilityPrototype):

    TYPE = ABILITY_TYPE.NONBATTLE
    ACTIVATION_TYPE = ABILITY_ACTIVATION_TYPE.PASSIVE
    AVAILABILITY = ABILITY_AVAILABILITY.FOR_PLAYERS

    NAME = u'Торгаш'
    normalized_name = NAME
    DESCRIPTION = u'Увеличивается цена продажи и уменьшается цена покупки предметов.'

    SELL_MULTIPLIER = 1.2
    BUY_MULTIPLIER = 0.8

    def update_buy_price(self, hero, money):
        return int(money * self.BUY_MULTIPLIER)

    def update_sell_price(self, hero, money):
        ''' +1 for increase price on low levels'''
        return int(money * self.SELL_MULTIPLIER + 1)


ABILITIES = dict( (ability.get_id(), ability)
                  for ability in globals().values()
                  if isinstance(ability, type) and issubclass(ability, AbilityPrototype) and ability != AbilityPrototype)
