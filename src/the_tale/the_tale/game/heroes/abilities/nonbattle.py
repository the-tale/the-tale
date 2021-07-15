
import smart_imports

smart_imports.all()


# Денежный способности расчитываем так, чтобы они увеличивали скорость прироста денег по отношению к скорости трат на константу
MAX_MONEY_ABILITIES_BONUS = 1.5


class CHARISMA(prototypes.AbilityPrototype):

    TYPE = relations.ABILITY_TYPE.NONBATTLE
    ACTIVATION_TYPE = relations.ABILITY_ACTIVATION_TYPE.PASSIVE
    AVAILABILITY = relations.ABILITY_AVAILABILITY.FOR_PLAYERS

    NAME = 'Харизматичный'
    normalized_name = NAME
    DESCRIPTION = 'Герой настолько обаятелен, что умудряется получать лучшие награды за выполнение заданий.'

    @property
    def money_bonus(self):
        QUESTS_FRACTION = c.EXPECTED_QUESTS_IN_DAY / f.artifacts_in_day()
        ARTIFACTS_FRACTION = 1 - QUESTS_FRACTION

        # MAX_MONEY_ABILITIES_BONUS = c.INCOME_LOOT_FRACTION + c.INCOME_ARTIFACTS_FRACTION * (artifacts_fraction + TOTAL_BONUS * quests_fraction)
        # (MAX_MONEY_ABILITIES_BONUS - c.INCOME_LOOT_FRACTION) / c.INCOME_ARTIFACTS_FRACTION  = artifacts_fraction + TOTAL_BONUS * quests_fraction
        # (MAX_MONEY_ABILITIES_BONUS - c.INCOME_LOOT_FRACTION) / c.INCOME_ARTIFACTS_FRACTION - artifacts_fraction = TOTAL_BONUS * quests_fraction
        # MAX_MONEY_ABILITIES_BONUS заменяем на 1 + self.MONEY_BONUS[self.level-1]
        TOTAL_BONUS = ((MAX_MONEY_ABILITIES_BONUS - c.INCOME_LOOT_FRACTION) / c.INCOME_ARTIFACTS_FRACTION - ARTIFACTS_FRACTION) / QUESTS_FRACTION

        return self.level * (TOTAL_BONUS - 1) / 5.0

    def modify_attribute(self, type_, value): return value + self.money_bonus if type_.is_QUEST_MONEY_REWARD else value


# Для этой способности важно не делать бонус к покупке большим, иначе она будет давать слишком большой бонус в сочетании со всеми другим эффектами увеличения дохода
class HUCKSTER(prototypes.AbilityPrototype):

    TYPE = relations.ABILITY_TYPE.NONBATTLE
    ACTIVATION_TYPE = relations.ABILITY_ACTIVATION_TYPE.PASSIVE
    AVAILABILITY = relations.ABILITY_AVAILABILITY.FOR_PLAYERS

    NAME = 'Торгаш'
    normalized_name = NAME
    DESCRIPTION = 'Увеличивается цена продажи и уменьшаются все траты.'

    BUY_BONUS = [-0.025, -0.050, -0.075, -0.10, -0.125]

    @property
    def buy_bonus(self): return self.BUY_BONUS[self.level - 1]

    @classmethod
    def _sell_bonus(self, level):
        # MAX_MONEY_ABILITIES_BONUS = c.INCOME_LOOT_FRACTION * TOTAL_BONUS + c.INCOME_ARTIFACTS_FRACTION
        # TOTAL_BONUS = (MAX_MONEY_ABILITIES_BONUS - c.INCOME_ARTIFACTS_FRACTION) / c.INCOME_LOOT_FRACTION
        # MAX_MONEY_ABILITIES_BONUS пересчиываем с учётом скидки на покупку -> (1+BUY_BONUS[-1]) * MAX_MONEY_ABILITIES_BONUS
        MAX_BONUS = (1 + self.BUY_BONUS[-1]) * MAX_MONEY_ABILITIES_BONUS
        return ((MAX_BONUS - c.INCOME_ARTIFACTS_FRACTION) / c.INCOME_LOOT_FRACTION - 1) / 5.0 * level

    @property
    def sell_bonus(self):
        return self._sell_bonus(level=self.level)

    def modify_attribute(self, type_, value):
        if type_.is_BUY_PRICE:
            return value + self.buy_bonus

        if type_.is_SELL_PRICE:
            # +1 for increase price on low levels
            return value + self.sell_bonus

        return value


class DANDY(prototypes.AbilityPrototype):

    TYPE = relations.ABILITY_TYPE.NONBATTLE
    ACTIVATION_TYPE = relations.ABILITY_ACTIVATION_TYPE.PASSIVE
    AVAILABILITY = relations.ABILITY_AVAILABILITY.FOR_PLAYERS

    NAME = 'Щёголь'
    normalized_name = NAME
    DESCRIPTION = 'Увеличивает вероятность траты денег на заточку, ремонт и покупку артефактов.'

    PRIORITY_MULTIPLIER = [1.4, 1.8, 2.2, 2.6, 3.0]

    @property
    def priority_multiplier(self): return self.PRIORITY_MULTIPLIER[self.level - 1]

    def modify_attribute(self, type_, value):
        if type_.is_ITEMS_OF_EXPENDITURE_PRIORITIES:
            value[heroes_relations.ITEMS_OF_EXPENDITURE.BUYING_ARTIFACT] *= self.priority_multiplier
            value[heroes_relations.ITEMS_OF_EXPENDITURE.SHARPENING_ARTIFACT] *= self.priority_multiplier
            value[heroes_relations.ITEMS_OF_EXPENDITURE.REPAIRING_ARTIFACT] *= self.priority_multiplier
        return value


class BUSINESSMAN(prototypes.AbilityPrototype):

    TYPE = relations.ABILITY_TYPE.NONBATTLE
    ACTIVATION_TYPE = relations.ABILITY_ACTIVATION_TYPE.PASSIVE
    AVAILABILITY = relations.ABILITY_AVAILABILITY.FOR_PLAYERS

    NAME = 'Делец'
    normalized_name = NAME
    DESCRIPTION = 'Герой имеет больше шансов получить артефакт в награду за выполнение задания.'

    PROBABILITY = [0.04, 0.08, 0.12, 0.16, 0.20]

    @property
    def probability(self): return self.PROBABILITY[self.level - 1]

    def modify_attribute(self, type_, value): return (value + self.probability) if type_.is_GET_ARTIFACT_FOR_QUEST else value


class PICKY(prototypes.AbilityPrototype):

    TYPE = relations.ABILITY_TYPE.NONBATTLE
    ACTIVATION_TYPE = relations.ABILITY_ACTIVATION_TYPE.PASSIVE
    AVAILABILITY = relations.ABILITY_AVAILABILITY.FOR_PLAYERS

    NAME = 'Придирчивый'
    normalized_name = NAME
    DESCRIPTION = 'Герой с большей вероятностью получает редкие и эпические артефакты.'

    PROBABILITY = [1.4, 1.8, 2.2, 2.6, 3.0]

    @property
    def probability(self): return self.PROBABILITY[self.level - 1]

    def modify_attribute(self, type_, value):
        if type_.is_RARE:
            return value * self.probability
        if type_.is_EPIC:
            return value * self.probability
        return value


class WANDERER(prototypes.AbilityPrototype):

    TYPE = relations.ABILITY_TYPE.NONBATTLE
    ACTIVATION_TYPE = relations.ABILITY_ACTIVATION_TYPE.PASSIVE
    AVAILABILITY = relations.ABILITY_AVAILABILITY.FOR_PLAYERS

    NAME = 'Бродяга'
    normalized_name = NAME
    DESCRIPTION = 'Бродяги истоптали тысячи тропинок и всегда найдут кратчайшую дорогу, поэтому путешествуют быстрее остальных.'

    # since experience not depends on time, this agruments MUST be equal or less then GIFTER.EXPERIENCE_MULTIPLIER
    # in other case, GIFTED will give less experience, then WANDERER
    SPEED_MULTIPLIER = [1.03, 1.06, 1.09, 1.12, 1.15]

    @property
    def speed_multiplier(self): return self.SPEED_MULTIPLIER[self.level - 1]

    def modify_attribute(self, type_, value): return value * self.speed_multiplier if type_.is_SPEED else value


class GIFTED(prototypes.AbilityPrototype):

    TYPE = relations.ABILITY_TYPE.NONBATTLE
    ACTIVATION_TYPE = relations.ABILITY_ACTIVATION_TYPE.PASSIVE
    AVAILABILITY = relations.ABILITY_AVAILABILITY.FOR_PLAYERS

    NAME = 'Одарённый'
    normalized_name = NAME
    DESCRIPTION = 'Одарённые герои быстрее получают опыт.'

    EXPERIENCE_MULTIPLIER = [1.04, 1.08, 1.12, 1.16, 1.2]

    @property
    def experience_multiplier(self): return self.EXPERIENCE_MULTIPLIER[self.level - 1]

    def modify_attribute(self, type_, value): return value * self.experience_multiplier if type_.is_EXPERIENCE else value


class DIPLOMATIC(prototypes.AbilityPrototype):

    TYPE = relations.ABILITY_TYPE.NONBATTLE
    ACTIVATION_TYPE = relations.ABILITY_ACTIVATION_TYPE.PASSIVE
    AVAILABILITY = relations.ABILITY_AVAILABILITY.FOR_PLAYERS

    MAXIMUM_MULTIPLIER = tt_politic_power_constants.MODIFIER_HERO_ABILITIES

    NAME = 'Дипломатичный'
    normalized_name = NAME
    DESCRIPTION = 'Некоторые герои приноровились выполнять задание особенно хитро и тщательно, тем самым увеличивая своё влияние на участников задания. Максимальный бонус к влиянию: %d%%' % (MAXIMUM_MULTIPLIER * 100)

    @property
    def power_multiplier(self):
        return self.MAXIMUM_MULTIPLIER * self.level / 5

    def modify_attribute(self, type_, value): return value + self.power_multiplier if type_.is_POWER else value


class THRIFTY(prototypes.AbilityPrototype):

    TYPE = relations.ABILITY_TYPE.NONBATTLE
    ACTIVATION_TYPE = relations.ABILITY_ACTIVATION_TYPE.PASSIVE
    AVAILABILITY = relations.ABILITY_AVAILABILITY.FOR_PLAYERS

    NAME = 'Запасливый'
    normalized_name = NAME
    DESCRIPTION = 'Запасливый герой не любит расставаться с добычей, поэтому носит с собой рюкзак большего размера.'

    MAX_BAG_SIZE_MODIFIER = [2, 3, 4, 5, 6]

    @property
    def max_bag_size_modifier(self): return self.MAX_BAG_SIZE_MODIFIER[self.level - 1]

    def modify_attribute(self, type_, value):
        return value + self.max_bag_size_modifier if type_.is_MAX_BAG_SIZE else value


class OPEN_MINDED(prototypes.AbilityPrototype):

    TYPE = relations.ABILITY_TYPE.NONBATTLE
    ACTIVATION_TYPE = relations.ABILITY_ACTIVATION_TYPE.PASSIVE
    AVAILABILITY = relations.ABILITY_AVAILABILITY.FOR_PLAYERS

    NAME = 'Открытый'
    normalized_name = NAME
    DESCRIPTION = 'Герой всегда готов посмотреть на вещи с новой стороны, благодаря чему увеличивается скорость изменения его черт.'

    HABIT_MULTIPLIER = [1.2, 1.4, 1.6, 1.8, 2.0]

    @property
    def habit_multiplier(self): return self.HABIT_MULTIPLIER[self.level - 1]

    def modify_attribute(self, type_, value):
        return value * self.habit_multiplier if type_.is_HABITS_INCREASE else value


class SELFISH(prototypes.AbilityPrototype):

    TYPE = relations.ABILITY_TYPE.NONBATTLE
    ACTIVATION_TYPE = relations.ABILITY_ACTIVATION_TYPE.PASSIVE
    AVAILABILITY = relations.ABILITY_AVAILABILITY.FOR_PLAYERS

    NAME = 'Эгоцентричный'
    normalized_name = NAME
    DESCRIPTION = 'Герой чаще выбирает задания, связанные со своими предпочтениями.'

    MULTIPLIER = [0.2, 0.4, 0.6, 0.8, 1.0]

    @property
    def multiplier(self): return self.MULTIPLIER[self.level - 1]

    def modify_attribute(self, type_, value):
        return value + self.multiplier if type_.is_CHARACTER_QUEST_PRIORITY else value


ABILITIES = dict((ability.get_id(), ability)
                 for ability in globals().values()
                 if (isinstance(ability, type) and
                     issubclass(ability, prototypes.AbilityPrototype) and
                     ability != prototypes.AbilityPrototype))
