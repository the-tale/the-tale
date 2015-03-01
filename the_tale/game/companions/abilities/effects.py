# coding: utf-8
from rels import Column
from rels.django import DjangoEnum

from the_tale.game import relations as game_relations

from the_tale.game.balance import constants as c

from the_tale.game.heroes import relations as heroes_relations
from the_tale.game.heroes.habilities import battle as battle_abilities

from the_tale.game.companions.abilities import relations


class Base(object):
    TYPE = None

    def __init__(self):
        pass

    @property
    def uid(self):
        return (self.TYPE, None)

    def modify_attribute(self, abilities_levels, modifier, value):
        return self._modify_attribute(abilities_levels, modifier, value)

    def check_attribute(self, modifier):
        return self._check_attribute(modifier)

    def _modify_attribute(self, abilities_levels, modifier, value):
        return value

    def _check_attribute(self, modifier):
        return False


class NoEffect(Base):
    TYPE = None

class Checker(Base):
    MODIFIER = None

    def _check_attribute(self, modifier):
        return modifier == self.MODIFIER

def aprox(left, right, level):
    return left + float(right - left) / 5 * level

class Multiplier(Base):
    MODIFIER = None

    def __init__(self, multiplier_left, multiplier_right=None):
        super(Multiplier, self).__init__()
        self.multiplier_left = multiplier_left
        self.multiplier_right = multiplier_right if multiplier_right is not None else multiplier_left

    def _modify_attribute(self, abilities_levels, modifier, value):
        if modifier == self.MODIFIER:
            return value * aprox(self.multiplier_left,
                                 self.multiplier_right,
                                 abilities_levels.get(self.TYPE.metatype, 0))
        return value


class MultiplierChecker(Base):
    MODIFIER = None
    CHECK_MODIFIER = None

    def __init__(self, multiplier_left, multiplier_right=None):
        super(MultiplierChecker, self).__init__()
        self.multiplier_left = multiplier_left
        self.multiplier_right = multiplier_right if multiplier_right is not None else multiplier_left

    def _modify_attribute(self, abilities_levels, modifier, value):
        if modifier == self.MODIFIER:
            return value * aprox(self.multiplier_left,
                                 self.multiplier_right,
                                 abilities_levels.get(self.TYPE.metatype, 0))
        return value

    def _check_attribute(self, modifier):
        return modifier == self.CHECK_MODIFIER


class Summand(Base):
    MODIFIER = None

    def __init__(self, summand_left, summand_right=None):
        super(Summand, self).__init__()
        self.summand_left = summand_left
        self.summand_right = summand_right if summand_right is not None else summand_left

    def _modify_attribute(self, abilities_levels, modifier, value):
        if modifier == self.MODIFIER:
            return value + aprox(self.summand_left,
                                 self.summand_right,
                                 abilities_levels.get(self.TYPE.metatype, 0))
        return value



class CoherenceSpeed(Multiplier):
    TYPE = relations.EFFECT.COHERENCE_SPEED
    MODIFIER = heroes_relations.MODIFIERS.COHERENCE_EXPERIENCE


class ChangeHabits(Base):
    TYPE = relations.EFFECT.CHANGE_HABITS

    def __init__(self, habit_type, habit_sources, **kwargs):
        super(ChangeHabits, self).__init__(**kwargs)
        self.habit_type = habit_type
        self.habit_sources = frozenset(habit_sources)

    @property
    def uid(self):
        return (self.TYPE, self.habit_type)

    def _modify_attribute(self, abilities_levels, modifier, value):
        if modifier.is_HABITS_SOURCES:
            return value | self.habit_sources
        return value


class QuestMoneyReward(Multiplier):
    TYPE = relations.EFFECT.QUEST_MONEY_REWARD
    MODIFIER = heroes_relations.MODIFIERS.QUEST_MONEY_REWARD


class MaxBagSize(Summand):
    TYPE = relations.EFFECT.MAX_BAG_SIZE
    MODIFIER = heroes_relations.MODIFIERS.MAX_BAG_SIZE


class PoliticsPower(Multiplier):
    TYPE = relations.EFFECT.POLITICS_POWER
    MODIFIER = heroes_relations.MODIFIERS.POWER


class MagicDamageBonus(Multiplier):
    TYPE = relations.EFFECT.MAGIC_DAMAGE_BONUS
    MODIFIER = heroes_relations.MODIFIERS.MAGIC_DAMAGE

class PhysicDamageBonus(Multiplier):
    TYPE = relations.EFFECT.PHYSIC_DAMAGE_BONUS
    MODIFIER = heroes_relations.MODIFIERS.PHYSIC_DAMAGE

class Speed(Multiplier):
    TYPE = relations.EFFECT.SPEED
    MODIFIER = heroes_relations.MODIFIERS.SPEED


class BaseBattleAbility(Base):
    TYPE = None
    ABILITY = None

    def _modify_attribute(self, abilities_levels, modifier, value):
        if modifier.is_INITIATIVE:
            return value * (1 + aprox(c.COMPANIONS_BATTLE_STRIKE_PROBABILITY / 2,
                                      c.COMPANIONS_BATTLE_STRIKE_PROBABILITY,
                                      abilities_levels.get(self.TYPE.metatype, 0)))
        if modifier.is_ADDITIONAL_ABILITIES:
            value.append(self.ABILITY)
            return value
        return value

class BattleAbilityHit(BaseBattleAbility):
    TYPE = relations.EFFECT.BATTLE_ABILITY_HIT
    ABILITY = battle_abilities.HIT(1)

class BattleAbilityStrongHit(BaseBattleAbility):
    TYPE = relations.EFFECT.BATTLE_ABILITY_STRONG_HIT
    ABILITY = battle_abilities.STRONG_HIT(5)

class BattleAbilityRunUpPush(BaseBattleAbility):
    TYPE = relations.EFFECT.BATTLE_ABILITY_RUN_UP_PUSH
    ABILITY = battle_abilities.RUN_UP_PUSH(5)

class BattleAbilityFireball(BaseBattleAbility):
    TYPE = relations.EFFECT.BATTLE_ABILITY_FIREBALL
    ABILITY = ability=battle_abilities.FIREBALL(5)

class BattleAbilityPoisonCloud(BaseBattleAbility):
    TYPE = relations.EFFECT.BATTLE_ABILITY_POSION_CLOUD
    ABILITY = battle_abilities.POISON_CLOUD(5)

class BattleAbilityFreezing(BaseBattleAbility):
    TYPE = relations.EFFECT.BATTLE_ABILITY_FREEZING
    ABILITY = battle_abilities.FREEZING(5)


class Initiative(Multiplier):
    TYPE = relations.EFFECT.INITIATIVE
    MODIFIER = heroes_relations.MODIFIERS.INITIATIVE


class BattleProbability(Summand):
    TYPE = relations.EFFECT.BATTLE_PROBABILITY
    MODIFIER = heroes_relations.MODIFIERS.BATTLES_PER_TURN

class Deathy(BattleProbability):
    TYPE = relations.EFFECT.DEATHY
    MODIFIER = heroes_relations.MODIFIERS.BATTLES_PER_TURN


class LootProbability(Multiplier):
    TYPE = relations.EFFECT.LOOT_PROBABILITY
    MODIFIER = heroes_relations.MODIFIERS.LOOT_PROBABILITY


class Unsociable(Summand):
    TYPE = relations.EFFECT.LEAVE_HERO
    MODIFIER = heroes_relations.MODIFIERS.COMPANION_LEAVE_IN_PLACE


class CompanionDamage(Summand):
    TYPE = relations.EFFECT.COMPANION_DAMAGE
    MODIFIER = heroes_relations.MODIFIERS.COMPANION_DAMAGE

class CompanionDamageProbability(Multiplier):
    TYPE = relations.EFFECT.COMPANION_DAMAGE_PROBABILITY
    MODIFIER = heroes_relations.MODIFIERS.COMPANION_DAMAGE_PROBABILITY


class CompanionStealMoney(MultiplierChecker):
    TYPE = relations.EFFECT.COMPANION_STEAL_MONEY
    MODIFIER = heroes_relations.MODIFIERS.COMPANION_STEAL_MONEY_MULTIPLIER
    CHECK_MODIFIER = heroes_relations.MODIFIERS.COMPANION_STEAL_MONEY

class CompanionStealItem(MultiplierChecker):
    TYPE = relations.EFFECT.COMPANION_STEAL_ITEM
    MODIFIER = heroes_relations.MODIFIERS.COMPANION_STEAL_ITEM_MULTIPLIER
    CHECK_MODIFIER = heroes_relations.MODIFIERS.COMPANION_STEAL_ITEM


class CompanionSpareParts(Checker):
    TYPE = relations.EFFECT.COMPANION_SPARE_PARTS
    MODIFIER = heroes_relations.MODIFIERS.COMPANION_SPARE_PARTS


class CompanionSayWisdom(MultiplierChecker):
    TYPE = relations.EFFECT.COMPANION_EXPERIENCE
    MODIFIER = heroes_relations.MODIFIERS.COMPANION_SAY_WISDOM_PROBABILITY
    CHECK_MODIFIER = heroes_relations.MODIFIERS.COMPANION_SAY_WISDOM


class CompanionExpPerHeal(MultiplierChecker):
    TYPE = relations.EFFECT.COMPANION_EXPERIENCE
    MODIFIER = heroes_relations.MODIFIERS.COMPANION_EXP_PER_HEAL_PROBABILITY
    CHECK_MODIFIER = heroes_relations.MODIFIERS.COMPANION_EXP_PER_HEAL


class DoubleEnergyRegeneration(Summand):
    TYPE = relations.EFFECT.COMPANION_DOUBLE_ENERGY_REGENERATION
    MODIFIER = heroes_relations.MODIFIERS.DOUBLE_ENERGY_REGENERATION


class CompanionEatCorpses(MultiplierChecker):
    TYPE = relations.EFFECT.COMPANION_REGENERATION
    MODIFIER = heroes_relations.MODIFIERS.COMPANION_EAT_CORPSES_PROBABILITY
    CHECK_MODIFIER = heroes_relations.MODIFIERS.COMPANION_EAT_CORPSES

class CompanionRegenerate(MultiplierChecker):
    TYPE = relations.EFFECT.COMPANION_REGENERATION
    MODIFIER = heroes_relations.MODIFIERS.COMPANION_REGENERATE_PROBABILITY
    CHECK_MODIFIER = heroes_relations.MODIFIERS.COMPANION_REGENERATE


class CompanionEat(Multiplier):
    TYPE = relations.EFFECT.COMPANION_EAT
    MODIFIER = heroes_relations.MODIFIERS.COMPANION_MONEY_FOR_FOOD

    def _check_attribute(self, modifier):
        return modifier == self.MODIFIER

class CompanionEatDiscount(CompanionEat):
    TYPE = relations.EFFECT.COMPANION_EAT_DISCOUNT


class CompanionDrinkArtifact(MultiplierChecker):
    TYPE = relations.EFFECT.COMPANION_DRINK_ARTIFACT
    MODIFIER = heroes_relations.MODIFIERS.COMPANION_DRINK_ARTIFACT_PROBABILITY
    CHECK_MODIFIER = heroes_relations.MODIFIERS.COMPANION_DRINK_ARTIFACT


class CompanionExorcist(MultiplierChecker):
    TYPE = relations.EFFECT.COMPANION_EXORCIST
    MODIFIER = heroes_relations.MODIFIERS.COMPANION_EXORCIST_PROBABILITY
    CHECK_MODIFIER = heroes_relations.MODIFIERS.COMPANION_EXORCIST


class RestLenght(Multiplier):
    TYPE = relations.EFFECT.REST_LENGTH
    MODIFIER = heroes_relations.MODIFIERS.REST_LENGTH


class IDLELenght(Multiplier):
    TYPE = relations.EFFECT.IDLE_LENGTH
    MODIFIER = heroes_relations.MODIFIERS.IDLE_LENGTH


class CompanionBlockProbability(Multiplier):
    TYPE = relations.EFFECT.COMPANION_BLOCK_PROBABILITY
    MODIFIER = heroes_relations.MODIFIERS.COMPANION_BLOCK_PROBABILITY


class Huckster(Multiplier):
    TYPE = relations.EFFECT.HUCKSTER

    def __init__(self, buy_multiplier_left, buy_multiplier_right, sell_multiplier_left, sell_multiplier_right):
        super(Multiplier, self).__init__()
        self.buy_multiplier_left = buy_multiplier_left
        self.buy_multiplier_right = buy_multiplier_right
        self.sell_multiplier_left = sell_multiplier_left
        self.sell_multiplier_right = sell_multiplier_right

    def _modify_attribute(self, abilities_levels, modifier, value):
        if modifier.is_BUY_PRICE:
            return value * aprox(self.buy_multiplier_left,
                                 self.buy_multiplier_right,
                                 abilities_levels.get(self.TYPE.metatype, 0))

        if modifier.is_SELL_PRICE:
            # +1 for increase price on low levels
            return value * aprox(self.sell_multiplier_left,
                                 self.sell_multiplier_right,
                                 abilities_levels.get(self.TYPE.metatype, 0)) + 1

        return value


class EtherealMagnet(Summand):
    TYPE = relations.EFFECT.MIGHT_CRIT_CHANCE
    MODIFIER = heroes_relations.MODIFIERS.MIGHT_CRIT_CHANCE


class CompanionTeleport(Summand):
    TYPE = relations.EFFECT.COMPANION_TELEPORTATION
    MODIFIER = heroes_relations.MODIFIERS.COMPANION_TELEPORTATOR

class CompanionFly(Summand):
    TYPE = relations.EFFECT.COMPANION_TELEPORTATION
    MODIFIER = heroes_relations.MODIFIERS.COMPANION_FLYER


class Rarity(NoEffect):
    TYPE = relations.EFFECT.RARITY


RARITY_LOW = -0.5
RARITY_LOWER = -1.0
RARITY_LOWEST = -2.0
RARITY_LOWEST_2 = -3.0

RARITY_NEUTRAL = 0.0

RARITY_BIG = 0.5
RARITY_BIGER = 1.0
RARITY_BIGEST = 2.0

RARITY_LEGENDARY = 666.0

class ABILITIES(DjangoEnum):
    description = Column()
    effect = Column(single_type=False)
    rarity_delta = Column(unique=False)

    records = (
        (u'OBSTINATE', 0, u'строптивый', u'слаженность растёт очень медленно', CoherenceSpeed(0.6), RARITY_LOWER),
        (u'STUBBORN', 1, u'упрямый', u'слаженность растёт медленнее обычного', CoherenceSpeed(0.8), RARITY_LOW),
        (u'BONA_FIDE', 2, u'добросовестный', u'слаженность растёт быстрее обычного', CoherenceSpeed(1.2), RARITY_BIG),
        (u'MANAGING', 3, u'исполнительный', u'слаженность растёт очень быстро', CoherenceSpeed(1.40), RARITY_BIGER),

        (u'AGGRESSIVE', 4, u'агрессивный', u'увеличивает агрессивность героя',
         ChangeHabits(habit_type=game_relations.HABIT_TYPE.PEACEFULNESS, habit_sources=(heroes_relations.HABIT_CHANGE_SOURCE.COMPANION_AGGRESSIVE, )), RARITY_NEUTRAL),
        (u'PEACEFUL', 5, u'миролюбивый', u'увеличивает миролюбие героя',
         ChangeHabits(habit_type=game_relations.HABIT_TYPE.PEACEFULNESS, habit_sources=(heroes_relations.HABIT_CHANGE_SOURCE.COMPANION_PEACEFULL,)), RARITY_NEUTRAL),
        (u'RESERVED', 6, u'сдержанный', u'склоняет героя к балансу между агрессивностью и миролюбием',
         ChangeHabits(habit_type=game_relations.HABIT_TYPE.PEACEFULNESS, habit_sources=(heroes_relations.HABIT_CHANGE_SOURCE.COMPANION_PEACEFULL_NEUTRAL_1,
                                                                                        heroes_relations.HABIT_CHANGE_SOURCE.COMPANION_PEACEFULL_NEUTRAL_2)), RARITY_NEUTRAL),
        (u'CANNY', 7, u'себе на уме', u'склоняет героя к балансу между честью и бесчестием',
         ChangeHabits(habit_type=game_relations.HABIT_TYPE.HONOR, habit_sources=(heroes_relations.HABIT_CHANGE_SOURCE.COMPANION_HONOR_NEUTRAL_1,
                                                                                 heroes_relations.HABIT_CHANGE_SOURCE.COMPANION_HONOR_NEUTRAL_2)), RARITY_NEUTRAL),
        (u'HONEST', 8, u'честный', u'увеличивает честь героя',
         ChangeHabits(habit_type=game_relations.HABIT_TYPE.HONOR, habit_sources=(heroes_relations.HABIT_CHANGE_SOURCE.COMPANION_HONORABLE,)), RARITY_NEUTRAL),
        (u'SNEAKY', 9, u'подлый', u'уменьшает честь героя',
         ChangeHabits(habit_type=game_relations.HABIT_TYPE.HONOR, habit_sources=(heroes_relations.HABIT_CHANGE_SOURCE.COMPANION_DISHONORABLE,)), RARITY_NEUTRAL),

        (u'CHARMING', 10, u'очаровательный', u'очень симпатичен горожанам, герой получает крупный бонус к денежной награде за задания', QuestMoneyReward(1.5, 3.0), RARITY_BIGER),
        (u'CUTE', 11, u'милый', u'симпатичен горожанам, герой получает небольшой бонус к денежной награда за задания', QuestMoneyReward(1.25, 1.5), RARITY_BIG),
        (u'FRIGHTFUL', 12, u'страшный', u'пугает горожан, герой получает меньше денег за задание', QuestMoneyReward(0.5, 0.75), RARITY_LOW),
        (u'TERRIBLE', 13, u'мороз по коже', u'сильно пугает горожан, герой получает значительно меньше денег в награду за задание.', QuestMoneyReward(0.30, 0.60), RARITY_LOWER),

        (u'PACK', 14, u'вьючный', u'2 дополнительных места в рюкзаке', MaxBagSize(2), RARITY_BIG),
        (u'FREIGHT', 15, u'грузовой', u'4 дополнительных места в рюкзаке', MaxBagSize(4), RARITY_BIGER),
        (u'DRAFT', 16, u'тягловой', u'6 дополнительных места в рюкзаке', MaxBagSize(6), RARITY_BIGEST),

        (u'PARAPHERNALIA', 55, u'личные вещи', u'забирает 2 места в рюкзаке для своих вещей', MaxBagSize(-2), RARITY_LOW),
        (u'SPARE_PARTS', 56, u'запчасти', u'забирает 4 места в рюкзаке для запчастей', MaxBagSize(-4), RARITY_LOWER),

        (u'KNOWN', 17, u'известный', u'находит политически важную работу, задания героя оказывают большее влияние на мир', PoliticsPower(1.5, 2.0), RARITY_BIGER),
        (u'CAD', 18, u'хам', u'хамит горожанам, герою не доверяют политически важную работу, поэтому он оказывает меньшее влияние на мир ', PoliticsPower(0.5, 0.75), RARITY_LOWER),

        (u'FIT_OF_ENERGY', 19, u'прилив сил', u'даёт небольшой бонус к физическому урону героя', MagicDamageBonus(1.05, 1.1), RARITY_BIGER),
        (u'PEP', 20, u'бодрость духа', u'даёт небольшой бонус к магическому урону героя', PhysicDamageBonus(1.05, 1.1), RARITY_BIGER),

        (u'SLOW', 22, u'медлительный', u'постоянный штраф к скорости героя', Speed(0.7, 0.85), RARITY_LOWER),
        (u'SEDATE', 68, u'степенный', u'постоянный небольшой штраф к скорости героя', Speed(0.8, 0.9), RARITY_LOW),
        (u'SLED', 21, u'ездовой', u'постоянный небольшой бонус к скорости героя', Speed(1.05, 1.10), RARITY_BIG),
        (u'RACER', 23, u'скакун', u'постоянный бонус к скорости героя', Speed(1.1, 1.15), RARITY_BIGER),
        (u'FLEET_FOOTED', 69, u'быстроногий', u'постоянный большой бонус к скорости героя', Speed(1.1, 1.2), RARITY_BIGEST),

        (u'FIGHTER', 24, u'боец', u'немного увеличивает инициативу героя, в бою может применить способность «Удар»', BattleAbilityHit(), RARITY_BIGER),
        (u'RAM', 25, u'громила', u'немного увеличивает инициативу героя, в бою может применить способность «Тяжёлый удар»', BattleAbilityStrongHit(), RARITY_BIGER),
        (u'HOUSEBREAKER', 26, u'таран', u'немного увеличивает инициативу героя, в бою может применить способность «Разбег-толчок»', BattleAbilityRunUpPush(), RARITY_BIGER),
        (u'ARSONIST', 27, u'поджигатель', u'немного увеличивает инициативу героя, в бою может применить способность «Огненный шар»', BattleAbilityFireball(), RARITY_BIGER),
        (u'POISONER', 28, u'отравитель', u'немного увеличивает инициативу героя, в бою может применить способность «Ядовитое облако»', BattleAbilityPoisonCloud(), RARITY_BIGER),
        (u'FROST', 29, u'морозко', u'немного увеличивает инициативу героя, в бою может применить способность «Заморозка»', BattleAbilityFreezing(), RARITY_BIGER),

        (u'UNGAINLY', 30, u'неуклюжий', u'большой штраф к инициативе героя', Initiative(0.8, 0.875), RARITY_LOWER),
        (u'CLUMSY', 31, u'неповоротливый', u'малый штраф к инициативе героя', Initiative(0.89, 0.94), RARITY_LOW),
        (u'CLEVER', 32, u'ловкий', u'малый бонус к инициативе героя', Initiative(1.01, 1.06), RARITY_BIGER),
        (u'IMPETUOUS', 33, u'стремительный', u'большой бонус к инициативе героя', Initiative(1.05, 1.125), RARITY_BIGER),

        (u'NOISY', 34, u'шумный', u'так сильно шумит, что привлекает внимание большего количества врагов', BattleProbability(0.2, 0.1), RARITY_LOWER),
        (u'SHARP_EYE', 36, u'острый глаз', u'издали высматривает врагов, снижая вероятность встречи с ними', BattleProbability(-0.05, -0.1), RARITY_BIGER),

        (u'DEATHY', 35, u'смертельно страшный', u'распугивает всех, кого встречает, вероятность встретить врага стремится к нулю', Deathy(-1), RARITY_BIGEST),

        (u'TORTURER', 37, u'терзатель', u'растерзывает врагов в бою так сильно, что уменьшается шанс найти уцелевшую в бою добычу', LootProbability(0.6, 0.8), RARITY_LOWER),
        (u'HUNTER', 38, u'охотник', u'помогает герою сражаться аккуратнее, благодаря чему увеличивает шанс найти уцелевшую в бою добычу', LootProbability(1.1, 1.2), RARITY_BIGER),

        (u'NOT_LIFER', 39, u'тщедушный', u'при ранении получает дополнительную единицу урона', CompanionDamage(1), RARITY_LOWER),
        (u'PUNY', 40, u'не жилец', u'при ранении получает 2 дополнительные единицы урона', CompanionDamage(2), RARITY_LOWEST),

        (u'CAMOUFLAGE', 41, u'камуфляж', u'благодаря незаметности, реже получает урон в бою', CompanionDamageProbability(0.9, 0.8), RARITY_BIGER),
        (u'FLYING', 42, u'летающий', u'перемещаясь не только вокруг но и над противником, значительно реже получает урон в бою', CompanionDamageProbability(0.85, 0.7), RARITY_BIGEST),

        (u'PICKPOCKET', 43, u'карманник', u'В каждом городе крадёт из карманов горожан немного денег', CompanionStealMoney(0.5, 3.0), RARITY_BIG),
        (u'ROBBER', 44, u'грабитель', u'В каждом городе крадёт у горожан что-нибудь полезное, возможно, даже экипировку', CompanionStealItem(1.05, 4.0), RARITY_BIGER),

        (u'COSTLY', 45, u'дорогой', u'при потере спутника герой получает весьма дорогие запчасти, обращаемые в деньги.', CompanionSpareParts(), RARITY_BIG),

        (u'WISE', 46, u'мудрый', u'спутник иногда делится мудростью с героем, давая тому немного опыта.', CompanionSayWisdom(0.5, 1.0), RARITY_BIGER),
        (u'DIFFICULT', 47, u'сложный', u'ухаживая за спутником, герой может получить немного опыта', CompanionExpPerHeal(0.5, 1.0), RARITY_BIGER),

        (u'FAN', 48, u'поклонник', u'возносит хвалу Хранителю вместе с героем и с небольшой вероятностью даёт бонусную энергию', DoubleEnergyRegeneration(0.05, 0.1), RARITY_BIGER),
        (u'SAN', 49, u'сан', u'возносит хвалу Хранителю вместе с героем и с хорошей вероятностью даёт бонусную энергию', DoubleEnergyRegeneration(0.1, 0.2), RARITY_BIGEST),

        (u'EAT_CORPSES', 50, u'пожиратель', u'после боя иногда ест труп врага, пополняя себе хиты. Не ест конструктов, нежить, демонов и стихийных существ.', CompanionEatCorpses(0.5, 1), RARITY_BIGER),
        (u'REGENERATE', 51, u'регенерация', u'во время отдыха может восстановить своё здоровье', CompanionRegenerate(0.5, 1.0), RARITY_BIGER),

        (u'EATER', 52, u'едок', u'при каждом посещении города герой тратит деньги на еду для спутника', CompanionEat(0.5, 0.25), RARITY_LOW),
        (u'GLUTTONOUS', 53, u'прожорливый', u'при каждом посещении города герой тратит много денег на еду для спутника', CompanionEat(0.7, 0.5), RARITY_LOWER),
        (u'INDEPENDENT', 54, u'самостоятельный', u'может кормиться сам, снижает стоимость кормёжки (способностей «едок» и «прожорливый»)', CompanionEatDiscount(0.9, 0.5), RARITY_BIG),

        (u'DRINKER', 57, u'пьяница', u'спутник пропивает случайный предмет из рюкзака при посещении героем города', CompanionDrinkArtifact(0.95, 0.5), RARITY_BIG),

        (u'EXORCIST', 58, u'экзорцист', u'спутник может изгнать встречного демона', CompanionExorcist(0.5, 1.0), RARITY_BIG),

        (u'HEALER', 59, u'лекарь', u'ускоряет лечение героя на отдыхе', RestLenght(0.9, 0.5), RARITY_BIGEST),

        (u'INSPIRATION', 60, u'воодушевление', u'воодушевляет героя на подвиги, снижая время бездействия между заданиями', IDLELenght(0.9, 0.5), RARITY_BIG),
        (u'LAZY', 61, u'ленивый', u'ленится вместе с героем и увеличивает время бездействия между заданиями', IDLELenght(2.0, 1.5), RARITY_LOW),

        (u'COWARDLY', 62, u'трусливый', u'реже защищает героя в бою', CompanionBlockProbability(0.5, 0.75), RARITY_NEUTRAL),
        (u'BODYGUARD', 63, u'телохранитель', u'чаще защищает героя в бою', CompanionBlockProbability(1.1, 1.25), RARITY_NEUTRAL),

        (u'HUCKSTER', 64, u'торгаш', u'помогает герою торговаться, увеличивая цены продажи и уменьшая цены покупки',
         Huckster(buy_multiplier_left=0.85, buy_multiplier_right=0.7, sell_multiplier_left=1.15, sell_multiplier_right=1.3), RARITY_BIG),

        (u'CONTACT', 65, u'связной', u'служит маяком для Хранителя и увеличивает шанс критической помощи', EtherealMagnet(0.05, 0.1), RARITY_BIGEST),

        (u'TELEPORTATOR', 66, u'телепортатор', u'периодически переносит героя между городами или ключевыми точками задания', CompanionTeleport(0.05, 0.1), RARITY_BIGEST),
        (u'FLYER', 67, u'ездовой летун', u'часто  переносит героя на небольшое расстояние по воздуху', CompanionFly(0.05, 0.1), RARITY_BIGEST),

        (u'UNCOMMON', 70, u'редкий', u'спутник встречается реже обычного', Rarity(), RARITY_BIGER),
        (u'RARE', 71, u'очень редкий', u'спутник встречается очень редко', Rarity(), RARITY_BIGEST),
        (u'SPECIAL', 72, u'особый', u'особый спутник, которого нельзя получить обычным способом', Rarity(), RARITY_LEGENDARY),

        (u'TEMPORARY', 73, u'временный', u'спутник с небольшой вероятностью может покинуть героя при посещении города',
         Unsociable(0.1 * c.COMPANIONS_LEAVE_IN_PLACE), RARITY_LOWEST),
        (u'UNSOCIABLE', 74, u'нелюдимый', u'спутник может покинуть героя при посещении городас ',
         Unsociable(c.COMPANIONS_LEAVE_IN_PLACE), RARITY_LOWEST_2),
    )
