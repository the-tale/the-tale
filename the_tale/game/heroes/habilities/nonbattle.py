# coding: utf-8
import random

from the_tale.game.heroes.habilities.prototypes import AbilityPrototype
from the_tale.game.heroes.habilities.relations import ABILITY_TYPE, ABILITY_ACTIVATION_TYPE, ABILITY_AVAILABILITY
from the_tale.game.heroes.relations import ITEMS_OF_EXPENDITURE


class CHARISMA(AbilityPrototype):

    TYPE = ABILITY_TYPE.NONBATTLE
    ACTIVATION_TYPE = ABILITY_ACTIVATION_TYPE.PASSIVE
    AVAILABILITY = ABILITY_AVAILABILITY.FOR_PLAYERS

    NAME = u'Харизматичный'
    normalized_name = NAME
    DESCRIPTION = u'Герой настолько обаятелен, что умудряется получать больше денег за выполнение заданий.'

    MONEY_MULTIPLIER = [2, 2.5, 3, 3.5, 4]

    @property
    def money_multiplier(self): return self.MONEY_MULTIPLIER[self.level-1]

    def modify_attribute(self, type_, value): return int(value * self.money_multiplier) if type_.is_QUEST_MONEY_REWARD else value


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
    def sell_multiplier(self): return self.SELL_MULTIPLIER[self.level-1]

    @property
    def buy_multiplier(self): return self.BUY_MULTIPLIER[self.level-1]

    def modify_attribute(self, type_, value):
        if type_.is_BUY_PRICE:
            return int(value * self.buy_multiplier)

        if type_.is_SELL_PRICE:
            # +1 for increase price on low levels
            return int(value * self.sell_multiplier + 1)

        return value


class DANDY(AbilityPrototype):

    TYPE = ABILITY_TYPE.NONBATTLE
    ACTIVATION_TYPE = ABILITY_ACTIVATION_TYPE.PASSIVE
    AVAILABILITY = ABILITY_AVAILABILITY.FOR_PLAYERS

    NAME = u'Щёголь'
    normalized_name = NAME
    DESCRIPTION = u'Увеличивает вероятность траты денег на заточку и покупку артефактов.'

    PRIORITY_MULTIPLIER = [1.5, 2, 2.5, 3, 3.5]

    @property
    def priority_multiplier(self): return self.PRIORITY_MULTIPLIER[self.level-1]

    def modify_attribute(self, type_, value):
        if type_.is_ITEMS_OF_EXPENDITURE_PRIORITIES:
            value[ITEMS_OF_EXPENDITURE.BUYING_ARTIFACT] *= self.priority_multiplier
            value[ITEMS_OF_EXPENDITURE.SHARPENING_ARTIFACT] *= self.priority_multiplier
        return value


class BUSINESSMAN(AbilityPrototype):

    TYPE = ABILITY_TYPE.NONBATTLE
    ACTIVATION_TYPE = ABILITY_ACTIVATION_TYPE.PASSIVE
    AVAILABILITY = ABILITY_AVAILABILITY.FOR_PLAYERS

    NAME = u'Делец'
    normalized_name = NAME
    DESCRIPTION = u'Герой может получить артефакт в награду за выполнение задания.'

    PROBABILITY = [0.025, 0.05, 0.075, 0.1, 0.125]

    @property
    def probability(self): return self.PROBABILITY[self.level-1]

    def check_attribute(self, type_):
        if type_.is_GET_ARTIFACT_FOR_QUEST:
            return random.uniform(0, 1) < self.probability


class PICKY(AbilityPrototype):

    TYPE = ABILITY_TYPE.NONBATTLE
    ACTIVATION_TYPE = ABILITY_ACTIVATION_TYPE.PASSIVE
    AVAILABILITY = ABILITY_AVAILABILITY.FOR_PLAYERS

    NAME = u'Придирчивый'
    normalized_name = NAME
    DESCRIPTION = u'Герой с большей вероятностью покупает полезные артефакты (лучше, чем экипированные).'

    PROBABILITY = [0.05, 0.1, 0.15, 0.2, 0.25]

    @property
    def probability(self): return self.PROBABILITY[self.level-1]

    def check_attribute(self, type_):
        if type_.is_BUY_BETTER_ARTIFACT:
            return random.uniform(0, 1) < self.probability


class ETHEREAL_MAGNET(AbilityPrototype):

    TYPE = ABILITY_TYPE.NONBATTLE
    ACTIVATION_TYPE = ABILITY_ACTIVATION_TYPE.PASSIVE
    AVAILABILITY = ABILITY_AVAILABILITY.FOR_PLAYERS

    NAME = u'Эфирный магнит'
    normalized_name = NAME
    DESCRIPTION = u'Герой притягивает к себе магию и увеличивает вероятность критического срабатывания помощи хранителя.'

    CRIT_PROBABILITY = [0.04, 0.08, 0.12, 0.16, 0.20]

    @property
    def crit_probability(self): return self.CRIT_PROBABILITY[self.level-1]

    def modify_attribute(self, type_, value): return min(1.0, value + self.crit_probability) if type_.is_MIGHT_CRIT_CHANCE else value


class WANDERER(AbilityPrototype):

    TYPE = ABILITY_TYPE.NONBATTLE
    ACTIVATION_TYPE = ABILITY_ACTIVATION_TYPE.PASSIVE
    AVAILABILITY = ABILITY_AVAILABILITY.FOR_PLAYERS

    NAME = u'Бродяга'
    normalized_name = NAME
    DESCRIPTION = u'Бродяги истоптали тысячи тропинок и всегда найдут кратчайшую дорогу, поэтому путешествуют быстрее остальных.'

    # since experience not depends on time, this agruments MUST be equal or less then GIFTER.EXPERIENCE_MULTIPLIER
    # in other case, GIFTED will give less experience, then WANDERER
    SPEED_MULTIPLIER = [1.04, 1.08, 1.12, 1.16, 1.20]

    @property
    def speed_multiplier(self): return self.SPEED_MULTIPLIER[self.level-1]

    def modify_attribute(self, type_, value): return value*self.speed_multiplier if type_.is_SPEED else value


class GIFTED(AbilityPrototype):

    TYPE = ABILITY_TYPE.NONBATTLE
    ACTIVATION_TYPE = ABILITY_ACTIVATION_TYPE.PASSIVE
    AVAILABILITY = ABILITY_AVAILABILITY.FOR_PLAYERS

    NAME = u'Одарённый'
    normalized_name = NAME
    DESCRIPTION = u'Одарённые герои быстрее получают опыт.'

    EXPERIENCE_MULTIPLIER = [1.05, 1.1, 1.15, 1.2, 1.25]

    @property
    def experience_multiplier(self): return self.EXPERIENCE_MULTIPLIER[self.level-1]

    def modify_attribute(self, type_, value): return value*self.experience_multiplier if type_.is_EXPERIENCE else value


class DIPLOMATIC(AbilityPrototype):

    TYPE = ABILITY_TYPE.NONBATTLE
    ACTIVATION_TYPE = ABILITY_ACTIVATION_TYPE.PASSIVE
    AVAILABILITY = ABILITY_AVAILABILITY.FOR_PLAYERS

    NAME = u'Дипломатичный'
    normalized_name = NAME
    DESCRIPTION = u'Некоторые герои приноровились выполнять задание особенно хитро и тщательно, тем самым увеличивая своё влияние на участников задания.'

    POWER_MULTIPLIER = [1.1, 1.2, 1.3, 1.4, 1.5]

    @property
    def power_multiplier(self): return self.POWER_MULTIPLIER[self.level-1]

    def modify_attribute(self, type_, value): return value*self.power_multiplier if type_.is_POWER else value


class THRIFTY(AbilityPrototype):

    TYPE = ABILITY_TYPE.NONBATTLE
    ACTIVATION_TYPE = ABILITY_ACTIVATION_TYPE.PASSIVE
    AVAILABILITY = ABILITY_AVAILABILITY.FOR_PLAYERS

    NAME = u'Запасливый'
    normalized_name = NAME
    DESCRIPTION = u'Запасливый герой не любит расставаться с добычей, поэтому носит с собой рюкзак большего размера.'

    MAX_BAG_SIZE_MODIFIER = [1, 2, 3, 4, 5]

    @property
    def max_bag_size_modifier(self): return self.MAX_BAG_SIZE_MODIFIER[self.level-1]

    def modify_attribute(self, type_, value): return value + self.max_bag_size_modifier if type_.is_MAX_BAG_SIZE else value


ABILITIES = dict( (ability.get_id(), ability)
                  for ability in globals().values()
                  if isinstance(ability, type) and issubclass(ability, AbilityPrototype) and ability != AbilityPrototype)
