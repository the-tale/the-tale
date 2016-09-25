# coding: utf-8

from the_tale.game.balance import constants as c
from the_tale.game.balance import formulas as f

from .prototypes import AbilityPrototype
from .relations import ABILITY_TYPE, ABILITY_ACTIVATION_TYPE, ABILITY_AVAILABILITY
from ..relations import ITEMS_OF_EXPENDITURE

# Денежный способности расчитываем так, чтобы они увеличивали скорость прироста денег по отношению к скорости трат на константу
MAX_MONEY_ABILITIES_BONUS = 1.5

class CHARISMA(AbilityPrototype):

    TYPE = ABILITY_TYPE.NONBATTLE
    ACTIVATION_TYPE = ABILITY_ACTIVATION_TYPE.PASSIVE
    AVAILABILITY = ABILITY_AVAILABILITY.FOR_PLAYERS

    NAME = u'Харизматичный'
    normalized_name = NAME
    DESCRIPTION = u'Герой настолько обаятелен, что умудряется получать лучшие награды за выполнение заданий.'

    QUESTS_FRACTION = c.EXPECTED_QUESTS_IN_DAY / f.artifacts_in_day()
    ARTIFACTS_FRACTION = 1 - QUESTS_FRACTION

    # MAX_MONEY_ABILITIES_BONUS = c.INCOME_LOOT_FRACTION + c.INCOME_ARTIFACTS_FRACTION * (artifacts_fraction + TOTAL_BONUS * quests_fraction)
    # (MAX_MONEY_ABILITIES_BONUS - c.INCOME_LOOT_FRACTION) / c.INCOME_ARTIFACTS_FRACTION  = artifacts_fraction + TOTAL_BONUS * quests_fraction
    # (MAX_MONEY_ABILITIES_BONUS - c.INCOME_LOOT_FRACTION) / c.INCOME_ARTIFACTS_FRACTION - artifacts_fraction = TOTAL_BONUS * quests_fraction
    # MAX_MONEY_ABILITIES_BONUS заменяем на 1 + self.MONEY_BONUS[self.level-1]
    TOTAL_BONUS = ((MAX_MONEY_ABILITIES_BONUS - c.INCOME_LOOT_FRACTION) / c.INCOME_ARTIFACTS_FRACTION - ARTIFACTS_FRACTION) / QUESTS_FRACTION

    MONEY_BONUS = [i * (TOTAL_BONUS - 1) / 5.0 for i in xrange(1, 6)]

    @property
    def money_bonus(self): return self.MONEY_BONUS[self.level-1]

    def modify_attribute(self, type_, value): return value + self.money_bonus if type_.is_QUEST_MONEY_REWARD else value


# Для этой способности важно не делать бонус к покупке большим, иначе она будет давать слишком большой бонус в сочетании со всеми другим эффектами увеличения дохода
class HUCKSTER(AbilityPrototype):

    TYPE = ABILITY_TYPE.NONBATTLE
    ACTIVATION_TYPE = ABILITY_ACTIVATION_TYPE.PASSIVE
    AVAILABILITY = ABILITY_AVAILABILITY.FOR_PLAYERS

    NAME = u'Торгаш'
    normalized_name = NAME
    DESCRIPTION = u'Увеличивается цена продажи и уменьшаются все траты.'

    BUY_BONUS = [-0.025, -0.050, -0.075, -0.10, -0.125]
    # MAX_MONEY_ABILITIES_BONUS = c.INCOME_LOOT_FRACTION * TOTAL_BONUS + c.INCOME_ARTIFACTS_FRACTION
    # TOTAL_BONUS = (MAX_MONEY_ABILITIES_BONUS - c.INCOME_ARTIFACTS_FRACTION) / c.INCOME_LOOT_FRACTION
    # MAX_MONEY_ABILITIES_BONUS пересчиываем с учётом скидки на покупку -> (1+BUY_BONUS[-1]) * MAX_MONEY_ABILITIES_BONUS
    MAX_BONUS = (1+BUY_BONUS[-1]) * MAX_MONEY_ABILITIES_BONUS
    SELL_BONUS = [((MAX_BONUS - c.INCOME_ARTIFACTS_FRACTION) / c.INCOME_LOOT_FRACTION - 1) / 5.0 * i for i in xrange(1, 6)]

    @property
    def buy_bonus(self): return self.BUY_BONUS[self.level-1]

    @property
    def sell_bonus(self): return self.SELL_BONUS[self.level-1]

    def modify_attribute(self, type_, value):
        if type_.is_BUY_PRICE:
            return value + self.buy_bonus

        if type_.is_SELL_PRICE:
            # +1 for increase price on low levels
            return value + self.sell_bonus

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

    PROBABILITY = [0.04, 0.08, 0.12, 0.16, 0.20]

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


class OPEN_MINDED(AbilityPrototype):

    TYPE = ABILITY_TYPE.NONBATTLE
    ACTIVATION_TYPE = ABILITY_ACTIVATION_TYPE.PASSIVE
    AVAILABILITY = ABILITY_AVAILABILITY.FOR_PLAYERS

    NAME = u'Открытый'
    normalized_name = NAME
    DESCRIPTION = u'Герой всегда готов посмотреть на вещи с новой стороны, благодаря чему увеличивается скорость изменения его черт.'

    HABIT_MULTIPLIER = [1.2, 1.4, 1.6, 1.8, 2.0]

    @property
    def habit_multiplier(self): return self.HABIT_MULTIPLIER[self.level-1]

    def modify_attribute(self, type_, value):
        return value * self.habit_multiplier if type_.is_HABITS_INCREASE else value


class SELFISH(AbilityPrototype):

    TYPE = ABILITY_TYPE.NONBATTLE
    ACTIVATION_TYPE = ABILITY_ACTIVATION_TYPE.PASSIVE
    AVAILABILITY = ABILITY_AVAILABILITY.FOR_PLAYERS

    NAME = u'Эгоцентричный'
    normalized_name = NAME
    DESCRIPTION = u'Герой чаще выбирает задания связанные со своими предпочтениями.'

    MULTIPLIER = [1.2, 1.4, 1.6, 1.8, 2.0]

    @property
    def multiplier(self): return self.MULTIPLIER[self.level-1]

    def modify_attribute(self, type_, value):
        return value * self.multiplier if type_.is_CHARACTER_QUEST_PRIORITY else value


ABILITIES = dict( (ability.get_id(), ability)
                  for ability in globals().values()
                  if isinstance(ability, type) and issubclass(ability, AbilityPrototype) and ability != AbilityPrototype)
