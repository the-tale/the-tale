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
            return value * (1 + aprox(c.COMPANION_BATTLE_STRIKE_PROBABILITY / 2,
                                      c.COMPANION_BATTLE_STRIKE_PROBABILITY,
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


class CompanionSpareParts(MultiplierChecker):
    TYPE = relations.EFFECT.COMPANION_SPARE_PARTS
    MODIFIER = heroes_relations.MODIFIERS.COMPANION_SPARE_PARTS_MULTIPLIER
    CHECK_MODIFIER = heroes_relations.MODIFIERS.COMPANION_SPARE_PARTS


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


class ABILITIES(DjangoEnum):
    description = Column()
    effect = Column(single_type=False)

    records = (
        (u'OBSTINATE', 0, u'строптивый', u'очень медленный рост слаженности', CoherenceSpeed(0.70)),
        (u'STUBBORN', 1, u'упрямый', u'медленный рост слаженности', CoherenceSpeed(0.85)),
        (u'BONA_FIDE', 2, u'добросовестный', u'быстрый рост слаженности', CoherenceSpeed(1.15)),
        (u'MANAGING', 3, u'исполнительный', u'очень быстрый рост слаженности', CoherenceSpeed(1.30)),

        (u'AGGRESSIVE', 4, u'агрессивный', u'повышает агрессивность героя',
         ChangeHabits(habit_type=game_relations.HABIT_TYPE.PEACEFULNESS, habit_sources=(heroes_relations.HABIT_CHANGE_SOURCE.COMPANION_AGGRESSIVE, ))),
        (u'PEACEFUL', 5, u'миролюбивый', u'понижает агрессивность героя',
         ChangeHabits(habit_type=game_relations.HABIT_TYPE.PEACEFULNESS, habit_sources=(heroes_relations.HABIT_CHANGE_SOURCE.COMPANION_PEACEFULL,))),
        (u'RESERVED', 6, u'сдержанный', u'склоняет героя к сдержанности',
         ChangeHabits(habit_type=game_relations.HABIT_TYPE.PEACEFULNESS, habit_sources=(heroes_relations.HABIT_CHANGE_SOURCE.COMPANION_PEACEFULL_NEUTRAL_1,
                                                                                        heroes_relations.HABIT_CHANGE_SOURCE.COMPANION_PEACEFULL_NEUTRAL_2))),
        (u'CANNY', 7, u'себе на уме', u'склоняет героя быть себе на уме',
         ChangeHabits(habit_type=game_relations.HABIT_TYPE.HONOR, habit_sources=(heroes_relations.HABIT_CHANGE_SOURCE.COMPANION_HONOR_NEUTRAL_1,
                                                                                 heroes_relations.HABIT_CHANGE_SOURCE.COMPANION_HONOR_NEUTRAL_2))),
        (u'HONEST', 8, u'честный', u'повышает честь героя',
         ChangeHabits(habit_type=game_relations.HABIT_TYPE.HONOR, habit_sources=(heroes_relations.HABIT_CHANGE_SOURCE.COMPANION_HONORABLE,))),
        (u'SNEAKY', 9, u'подлый', u'понижает честь героя',
         ChangeHabits(habit_type=game_relations.HABIT_TYPE.HONOR, habit_sources=(heroes_relations.HABIT_CHANGE_SOURCE.COMPANION_DISHONORABLE,))),

        (u'CHARMING', 10, u'очаровательный', u'симпатичен горожанам. Крупный бонус к денежной награде за квесты', QuestMoneyReward(1.5, 2.0)),
        (u'CUTE', 11, u'милый', u'симпатичен горожанам. Небольшой бонус к денежной награде за квесты', QuestMoneyReward(1.25, 1.5)),
        (u'FRIGHTFUL', 12, u'страшный', u'пугает горожан своим видом. Маленький штраф к оплате квестов.', QuestMoneyReward(0.70, 0.85)),
        (u'TERRIBLE', 13, u'мороз по коже', u'пугает горожан своим видом. Болшой штраф к оплате квестов.', QuestMoneyReward(0.50, 0.75)),

        (u'PACK', 14, u'вьючный', u'1 дополнительное место для лута', MaxBagSize(1)),
        (u'FREIGHT', 15, u'грузовой', u'2 дополнительных места для лута', MaxBagSize(2)),
        (u'DRAFT', 16, u'тягловой', u'3 дополнительных места для лута', MaxBagSize(3)),

        (u'KNOWN', 17, u'известный', u'находит более политически важную работу', PoliticsPower(1.25, 1.5)),
        (u'CAD', 18, u'хам', u'хамит горожанам. Минус к влиянию заданий', PoliticsPower(0.7, 0.85)),

        (u'FIT_OF_ENERGY', 19, u'прилив сил', u'бонус к физическому урону, наносимому героем', MagicDamageBonus(1.1, 1.2)),
        (u'PEP', 20, u'бодрость духа', u'бонус к магическому урону, наносимому героем', PhysicDamageBonus(1.1, 1.2)),

        (u'SLOW', 22, u'медлительный', u'постоянный штраф к скорости героя', Speed(0.7, 0.85)),
        (u'SEDATE', 68, u'степенный', u'постоянный небольшой штраф к скорости героя', Speed(0.8, 0.9)),
        (u'SLED', 21, u'ездовой', u'постоянный небольшой бонус к скорости героя', Speed(1.1, 1.2)),
        (u'RACER', 23, u'скакун', u'постоянный бонус к скорости героя', Speed(1.15, 1.3)),
        (u'FLEET_FOOTED', 69, u'быстроногий', u'постоянный большой бонус к скорости героя', Speed(1.2, 1.4)),

        (u'FIGHTER', 24, u'боец', u'увеличивает инициативу героя, в бою может применить способность «Удар»', BattleAbilityHit()),
        (u'RAM', 25, u'громила', u'увеличивает инициативу героя, в бою может применить способность «Тяжёлый удар»', BattleAbilityStrongHit()),
        (u'HOUSEBREAKER', 26, u'таран', u'увеличивает инициативу героя, в бою может применить способность «Разбег-толчок»', BattleAbilityRunUpPush()),
        (u'ARSONIST', 27, u'поджигатель', u'увеличивает инициативу героя, в бою может применить способность «Огненный шар»', BattleAbilityFireball()),
        (u'POISONER', 28, u'отравитель', u'увеличивает инициативу героя, в бою может применить способность «Ядовитое облако»', BattleAbilityPoisonCloud()),
        (u'FROST', 29, u'морозко', u'увеличивает инициативу героя, в бою может применить способность «Заморозка»', BattleAbilityFreezing()),


        (u'UNGAINLY', 30, u'неуклюжий', u'большой штраф к инициативе героя', Initiative(0.8, 0.9)),
        (u'CLUMSY', 31, u'неповоротливый', u'малый штраф к инициативе героя', Initiative(0.9, 0.95)),
        (u'CLEVER', 32, u'ловкий', u'малый бонус к инициативе героя', Initiative(1.05, 1.1)),
        (u'IMPETUOUS', 33, u'стремительный', u'большой бонус к инициативе героя', Initiative(1.1, 1.2)),

        (u'NOISY', 34, u'шумный', u'так сильно шумит, что привлекает внимание большего количесва врагов', BattleProbability(0.1, 0.05)),
        (u'SHARP_EYE', 36, u'зоркий глаз', u'издали высматривает врагов, снижая вероятность встречи с ними', BattleProbability(-0.05, -0.1)),

        (u'DEATHY', 35, u'смертельно страшный', u'распугивает чудищ, вероятность встретить врага стремится к нулю', Deathy(-1)),


        (u'TORTURER', 37, u'терзатель', u'растерзывает врагов в бою так сильно, что уменьшается шанс найти уцелевший лут с мобов', LootProbability(0.8, 0.9)),
        (u'HUNTER', 38, u'охотник', u'увеличивает шанс поднятия лута со всех врагов', LootProbability(1.1, 1.2)),

        (u'NOT_LIFER', 39, u'тщедушный', u'получает дополнительную едину урона', CompanionDamage(1)),
        (u'PUNY', 40, u'не жилец', u'получает дополнительные 2 единицы урона', CompanionDamage(2)),

        (u'CAMOUFLAGE', 41, u'камуфляж', u'реже получает урон в бою', CompanionDamageProbability(0.9, 0.8)),
        (u'FLYING', 42, u'летающий', u'значительно реже получает урон в бою', CompanionDamageProbability(0.85, 0.7)),

        (u'PICKPOCKET', 43, u'карманник', u'В каждом городе крадёт из карманов горожан немного денег', CompanionStealMoney(0.5, 2.0)),
        (u'ROBBER', 44, u'грабитель', u'В каждом городе крадёт у горожан что-нибудь, возможно артефакт', CompanionStealItem(0.5, 2.0)),

        (u'COSTLY', 45, u'дорогой', u'при потере спутника герой получает весьма дорогие запчасти, обращаемые в деньги.', CompanionSpareParts(0.5, 1)),

        (u'WISE', 46, u'мудрый', u'спутник иногда делится мудростью с героем, давая тому немного опыта.', CompanionSayWisdom(0.5, 1.0)),
        (u'DIFFICULT', 47, u'сложный', u'герой получает опыт каждый раз, когда ухаживает за спутником', CompanionExpPerHeal(0.5, 1.0)),

        (u'FAN', 48, u'поклонник', u'возносит хвалу Хранителю вместе с героем, с небольшой вероятностью даёт бонусную энергию', DoubleEnergyRegeneration(0.05, 0.1)),
        (u'SAN', 49, u'сан', u'возносит хвалу Хранителю вместе с героем, с хорошей вероятностью даёт бонусную энергию', DoubleEnergyRegeneration(0.1, 0.2)),

        (u'EAT_CORPSES', 50, u'пожиратель', u'иногда после боя ест труп врага, пополняя себе хиты. Не ест конструктов, нежить, демонов и стихийных.', CompanionEatCorpses(0.5, 1)),
        (u'REGENERATE', 51, u'регенерация', u'во время ухода за спутником может восстановить здоровье', CompanionRegenerate(0.5, 1.0)),

        (u'EATER', 52, u'едок', u'при каждом посещении города герой тратит деньги на еду для спутника', CompanionEat(0.5, 0.25)),
        (u'GLUTTONOUS', 53, u'прожорливый', u'при каждом посещении города герой тратит много денег на еду для спутника', CompanionEat(0.7, 0.5)),
        (u'INDEPENDENT', 54, u'самостоятельный', u'может кормиться сам, снижает стоимость кормёжки', CompanionEatDiscount(0.9, 0.5)),

        (u'PARAPHERNALIA', 55, u'личные вещи', u'минус 1 место в инвентаре (занятое вещами спутника)', MaxBagSize(-1)),
        (u'SPARE_PARTS', 56, u'запчасти', u'минус 2 места в инвентаре (занятые запчастями для спутника)', MaxBagSize(-2)),

        (u'DRINKER', 57, u'пьяница', u'спутник пропивает артефакт при посещении героем города', CompanionDrinkArtifact(0.95, 0.5)),

        (u'EXORCIST', 58, u'экзорцист', u'спутник изгоняет встречных демонов', CompanionExorcist(0.5, 1.0)),

        (u'HEALER', 59, u'лекарь', u'ускоряет лечение героя на отдыхе', RestLenght(0.9, 0.5)),

        (u'INSPIRATION', 60, u'воодушевление', u'воодушевляет героя на подвиги, снижая время бездействия между заданиями', IDLELenght(0.9, 0.5)),
        (u'LAZY', 61, u'ленивый', u'увеличивает время бездействия между заданиями', IDLELenght(2.0, 1.5)),

        (u'COWARDLY', 62, u'трусливый', u'реже защищает героя в бою', CompanionBlockProbability(0.7, 0.9)),
        (u'BODYGUARD', 63, u'телохранитель', u'чаще защищает героя в бою', CompanionBlockProbability(1.1, 1.25)),

        (u'HUCKSTER', 64, u'торгаш', u'бонус к ценам продажи и покупки', Huckster(buy_multiplier_left=0.9, buy_multiplier_right=0.8,
                                                                                  sell_multiplier_left=1.1, sell_multiplier_right=1.2)),

        (u'CONTACT', 65, u'связной', u'увеличивает шанс критической помощи хранителя', EtherealMagnet(0.05, 0.1)),

        (u'TELEPORTATOR', 66, u'телепортатор', u'периодически переносит героя между городами или ключевыми точками задания', CompanionTeleport(0.05, 0.1)),
        (u'FLYER', 67, u'ездовой летун', u'часто  переносит героя на небольшое расстоение по воздуху', CompanionFly(0.05, 0.1)),
    )
