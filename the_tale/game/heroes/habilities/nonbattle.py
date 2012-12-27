#coding: utf-8

from game.heroes.habilities.prototypes import AbilityPrototype, ABILITY_TYPE, ABILITY_ACTIVATION_TYPE, ABILITY_AVAILABILITY


class CHARISMA(AbilityPrototype):

    TYPE = ABILITY_TYPE.NONBATTLE
    ACTIVATION_TYPE = ABILITY_ACTIVATION_TYPE.PASSIVE
    AVAILABILITY = ABILITY_AVAILABILITY.FOR_PLAYERS

    NAME = u'Харизматичный'
    normalized_name = NAME
    DESCRIPTION = u'Герой настолько обаятелен, что умудряется получать лучшие награды за выполнение заданий.'

    MONEY_MULTIPLIER = [2, 2.5, 3, 3.5, 4]

    @property
    def money_multiplier(self): return self.MONEY_MULTIPLIER[self.level]

    def update_quest_reward(self, hero, money):
        return int(money * self.money_multiplier)


class HUCKSTER(AbilityPrototype):

    TYPE = ABILITY_TYPE.NONBATTLE
    ACTIVATION_TYPE = ABILITY_ACTIVATION_TYPE.PASSIVE
    AVAILABILITY = ABILITY_AVAILABILITY.FOR_PLAYERS

    NAME = u'Торгаш'
    normalized_name = NAME
    DESCRIPTION = u'Увеличивается цена продажи и уменьшается цена покупки предметов.'

    SELL_MULTIPLIER = [1.1, 1.15, 1.2, 1.25, 1.3]
    BUY_MULTIPLIER = [0.9, 0.85, 0.8, 0.75, 0.7]

    @property
    def sell_multiplier(self): return self.SELL_MULTIPLIER[self.level]

    @property
    def buy_multiplier(self): return self.BUY_MULTIPLIER[self.level]

    def update_buy_price(self, hero, money):
        return int(money * self.buy_multiplier)

    def update_sell_price(self, hero, money):
        ''' +1 for increase price on low levels'''
        return int(money * self.sell_multiplier + 1)


ABILITIES = dict( (ability.get_id(), ability)
                  for ability in globals().values()
                  if isinstance(ability, type) and issubclass(ability, AbilityPrototype) and ability != AbilityPrototype)
