# coding: utf-8
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

    MONEY_MULTIPLIER = [2, 4, 6, 8, 10]

    @property
    def money_multiplier(self): return self.MONEY_MULTIPLIER[self.level-1]

    def modify_attribute(self, type_, value): return value * self.money_multiplier if type_.is_QUEST_MONEY_REWARD else value


class HUCKSTER(AbilityPrototype):

    TYPE = ABILITY_TYPE.NONBATTLE
    ACTIVATION_TYPE = ABILITY_ACTIVATION_TYPE.PASSIVE
    AVAILABILITY = ABILITY_AVAILABILITY.FOR_PLAYERS

    NAME = u'Торгаш'
    normalized_name = NAME
    DESCRIPTION = u'Увеличивается цена продажи и уменьшается цена покупки предметов.'

    SELL_MULTIPLIER = [1.2, 1.4, 1.6, 1.8, 2.0]
    BUY_MULTIPLIER = [0.9, 0.8, 0.7, 0.6, 0.5]

    @property
    def sell_multiplier(self): return self.SELL_MULTIPLIER[self.level-1]

    @property
    def buy_multiplier(self): return self.BUY_MULTIPLIER[self.level-1]

    def modify_attribute(self, type_, value):
        if type_.is_BUY_PRICE:
            return value * self.buy_multiplier

        if type_.is_SELL_PRICE:
            # +1 for increase price on low levels
            return value * self.sell_multiplier + 1

        return value


class DANDY(AbilityPrototype):

    TYPE = ABILITY_TYPE.NONBATTLE
    ACTIVATION_TYPE = ABILITY_ACTIVATION_TYPE.PASSIVE
    AVAILABILITY = ABILITY_AVAILABILITY.FOR_PLAYERS

    NAME = u'Щёголь'
    normalized_name = NAME
    DESCRIPTION = u'Увеличивает вероятность траты денег на заточку, ремонт и покупку артефактов.'

    PRIORITY_MULTIPLIER = [1.4, 1.8, 2.2, 2.6, 3.0]

    @property
    def priority_multiplier(self): return self.PRIORITY_MULTIPLIER[self.level-1]

    def modify_attribute(self, type_, value):
        if type_.is_ITEMS_OF_EXPENDITURE_PRIORITIES:
            value[ITEMS_OF_EXPENDITURE.BUYING_ARTIFACT] *= self.priority_multiplier
            value[ITEMS_OF_EXPENDITURE.SHARPENING_ARTIFACT] *= self.priority_multiplier
            value[ITEMS_OF_EXPENDITURE.REPAIRING_ARTIFACT] *= self.priority_multiplier
        return value


class BUSINESSMAN(AbilityPrototype):

    TYPE = ABILITY_TYPE.NONBATTLE
    ACTIVATION_TYPE = ABILITY_ACTIVATION_TYPE.PASSIVE
    AVAILABILITY = ABILITY_AVAILABILITY.FOR_PLAYERS

    NAME = u'Делец'
    normalized_name = NAME
    DESCRIPTION = u'Герой имеет больше шансов получить артефакт в награду за выполнение задания.'

    PROBABILITY = [0.03, 0.06, 0.09, 0.12, 0.15]

    @property
    def probability(self): return self.PROBABILITY[self.level-1]

    def modify_attribute(self, type_, value): return (value + self.probability) if type_.is_GET_ARTIFACT_FOR_QUEST else value


class PICKY(AbilityPrototype):

    TYPE = ABILITY_TYPE.NONBATTLE
    ACTIVATION_TYPE = ABILITY_ACTIVATION_TYPE.PASSIVE
    AVAILABILITY = ABILITY_AVAILABILITY.FOR_PLAYERS

    NAME = u'Придирчивый'
    normalized_name = NAME
    DESCRIPTION = u'Герой с большей вероятностью получает редкие и эпические артефакты.'

    PROBABILITY = [1.4, 1.8, 2.2, 2.6, 3.0]

    @property
    def probability(self): return self.PROBABILITY[self.level-1]

    def modify_attribute(self, type_, value):
        if type_.is_RARE:
            return value * self.probability
        if type_.is_EPIC:
            return value * self.probability
        return value



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

    def modify_attribute(self, type_, value): return (value + self.crit_probability) if type_.is_MIGHT_CRIT_CHANCE else value


class WANDERER(AbilityPrototype):

    TYPE = ABILITY_TYPE.NONBATTLE
    ACTIVATION_TYPE = ABILITY_ACTIVATION_TYPE.PASSIVE
    AVAILABILITY = ABILITY_AVAILABILITY.FOR_PLAYERS

    NAME = u'Бродяга'
    normalized_name = NAME
    DESCRIPTION = u'Бродяги истоптали тысячи тропинок и всегда найдут кратчайшую дорогу, поэтому путешествуют быстрее остальных.'

    # since experience not depends on time, this agruments MUST be equal or less then GIFTER.EXPERIENCE_MULTIPLIER
    # in other case, GIFTED will give less experience, then WANDERER
    SPEED_MULTIPLIER = [1.03, 1.06, 1.09, 1.12, 1.15]

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

    EXPERIENCE_MULTIPLIER = [1.04, 1.08, 1.12, 1.16, 1.2]

    @property
    def experience_multiplier(self): return self.EXPERIENCE_MULTIPLIER[self.level-1]

    def modify_attribute(self, type_, value): return value*self.experience_multiplier if type_.is_EXPERIENCE else value


class DIPLOMATIC(AbilityPrototype):

    TYPE = ABILITY_TYPE.NONBATTLE
    ACTIVATION_TYPE = ABILITY_ACTIVATION_TYPE.PASSIVE
    AVAILABILITY = ABILITY_AVAILABILITY.FOR_PLAYERS

    MAXIMUM_MULTIPLIER = 2.0

    NAME = u'Дипломатичный'
    normalized_name = NAME
    DESCRIPTION = u'Некоторые герои приноровились выполнять задание особенно хитро и тщательно, тем самым увеличивая своё влияние на участников задания. Максимальный бонус к влиянию: %d%%' % (MAXIMUM_MULTIPLIER * 100)

    POWER_MULTIPLIER = [MAXIMUM_MULTIPLIER * i / 5 for i in xrange(1, 6)]

    @property
    def power_multiplier(self): return self.POWER_MULTIPLIER[self.level-1]

    def modify_attribute(self, type_, value): return value + self.power_multiplier if type_.is_POWER else value


class THRIFTY(AbilityPrototype):

    TYPE = ABILITY_TYPE.NONBATTLE
    ACTIVATION_TYPE = ABILITY_ACTIVATION_TYPE.PASSIVE
    AVAILABILITY = ABILITY_AVAILABILITY.FOR_PLAYERS

    NAME = u'Запасливый'
    normalized_name = NAME
    DESCRIPTION = u'Запасливый герой не любит расставаться с добычей, поэтому носит с собой рюкзак большего размера.'

    MAX_BAG_SIZE_MODIFIER = [2, 3, 4, 5, 6]

    @property
    def max_bag_size_modifier(self): return self.MAX_BAG_SIZE_MODIFIER[self.level-1]

    def modify_attribute(self, type_, value):
        return value + self.max_bag_size_modifier if type_.is_MAX_BAG_SIZE else value


ABILITIES = dict( (ability.get_id(), ability)
                  for ability in globals().values()
                  if isinstance(ability, type) and issubclass(ability, AbilityPrototype) and ability != AbilityPrototype)
