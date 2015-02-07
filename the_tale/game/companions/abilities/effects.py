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

    def modify_attribute(self, modifier, value):
        return self._modify_attribute(modifier, value)

    def check_attribute(self, modifier):
        return self._check_attribute(modifier)

    def _modify_attribute(self, modifier, value):
        return value

    def _check_attribute(self, modifier):
        return False


class Checker(Base):
    MODIFIER = None

    def _check_attribute(self, modifier):
        return modifier == self.MODIFIER


class Multiplier(Base):
    MODIFIER = None

    def __init__(self, multiplier):
        super(Multiplier, self).__init__()
        self.multiplier = multiplier

    def _modify_attribute(self, modifier, value):
        if modifier == self.MODIFIER:
            return value *self.multiplier
        return value


class Summand(Base):
    MODIFIER = None

    def __init__(self, summand):
        super(Summand, self).__init__()
        self.summand = summand

    def _modify_attribute(self, modifier, value):
        if modifier == self.MODIFIER:
            return value + self.summand
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

    def _modify_attribute(self, modifier, value):
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

    def _modify_attribute(self, modifier, value):
        if modifier.is_INITIATIVE:
            return value * (1 + c.COMPANION_BATTLE_STRIKE_PROBABILITY)
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


class LootProbability(Multiplier):
    TYPE = relations.EFFECT.LOOT_PROBABILITY
    MODIFIER = heroes_relations.MODIFIERS.LOOT_PROBABILITY


class CompanionDamage(Summand):
    TYPE = relations.EFFECT.COMPANION_DAMAGE
    MODIFIER = heroes_relations.MODIFIERS.COMPANION_DAMAGE

class CompanionDamageProbability(Multiplier):
    TYPE = relations.EFFECT.COMPANION_DAMAGE_PROBABILITY
    MODIFIER = heroes_relations.MODIFIERS.COMPANION_DAMAGE_PROBABILITY


class CompanionStealMoney(Checker):
    TYPE = relations.EFFECT.COMPANION_STEAL_MONEY
    MODIFIER = heroes_relations.MODIFIERS.COMPANION_STEAL_MONEY

class CompanionStealItem(Checker):
    TYPE = relations.EFFECT.COMPANION_STEAL_ITEM
    MODIFIER = heroes_relations.MODIFIERS.COMPANION_STEAL_ITEM

class CompanionSpareParts(Checker):
    TYPE = relations.EFFECT.COMPANION_SPARE_PARTS
    MODIFIER = heroes_relations.MODIFIERS.COMPANION_SPARE_PARTS


class CompanionSayWisdom(Checker):
    TYPE = relations.EFFECT.COMPANION_EXPERIENCE
    MODIFIER = heroes_relations.MODIFIERS.COMPANION_SAY_WISDOM

class CompanionExpPerHeal(Checker):
    TYPE = relations.EFFECT.COMPANION_EXPERIENCE
    MODIFIER = heroes_relations.MODIFIERS.COMPANION_EXP_PER_HEAL


class DoubleEnergyRegeneration(Summand):
    TYPE = relations.EFFECT.COMPANION_DOUBLE_ENERGY_REGENERATION
    MODIFIER = heroes_relations.MODIFIERS.DOUBLE_ENERGY_REGENERATION


class CompanionEatCorpses(Checker):
    TYPE = relations.EFFECT.COMPANION_REGENERATION
    MODIFIER = heroes_relations.MODIFIERS.COMPANION_EAT_CORPSES

class CompanionRegenerate(Checker):
    TYPE = relations.EFFECT.COMPANION_REGENERATION
    MODIFIER = heroes_relations.MODIFIERS.COMPANION_REGENERATE


class CompanionEat(Multiplier):
    TYPE = relations.EFFECT.COMPANION_EAT
    MODIFIER = heroes_relations.MODIFIERS.COMPANION_MONEY_FOR_FOOD

    def _check_attribute(self, modifier):
        return modifier == self.MODIFIER

class CompanionEatDiscount(CompanionEat):
    TYPE = relations.EFFECT.COMPANION_EAT_DISCOUNT


class CompanionDrinkArtifact(Checker):
    TYPE = relations.EFFECT.COMPANION_DRINK_ARTIFACT
    MODIFIER = heroes_relations.MODIFIERS.COMPANION_DRINK_ARTIFACT


class CompanionExorcist(Checker):
    TYPE = relations.EFFECT.COMPANION_EXORCIST
    MODIFIER = heroes_relations.MODIFIERS.COMPANION_EXORCIST


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

    def __init__(self, buy_multiplier, sell_multiplier):
        super(Multiplier, self).__init__()
        self.buy_multiplier = buy_multiplier
        self.sell_multiplier = sell_multiplier

    def _modify_attribute(self, modifier, value):
        if modifier.is_BUY_PRICE:
            return value * self.buy_multiplier

        if modifier.is_SELL_PRICE:
            # +1 for increase price on low levels
            return value * self.sell_multiplier + 1

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
    only_start = Column(unique=False)
    effect = Column(single_type=False)

    records = (
        (u'OBSTINATE', 0, u'строптивый', u'очень медленный рост слаженности', True, CoherenceSpeed(multiplier=0.70)),
        (u'STUBBORN', 1, u'упрямый', u'медленный рост слаженности', True, CoherenceSpeed(multiplier=0.85)),
        (u'BONA_FIDE', 2, u'добросовестный', u'быстрый рост слаженности', True, CoherenceSpeed(multiplier=1.15)),
        (u'MANAGING', 3, u'исполнительный', u'очень быстрый рост слаженности', True, CoherenceSpeed(multiplier=1.30)),

        (u'AGGRESSIVE', 4, u'агрессивный', u'повышает агрессивность героя', True,
         ChangeHabits(habit_type=game_relations.HABIT_TYPE.PEACEFULNESS, habit_sources=(heroes_relations.HABIT_CHANGE_SOURCE.COMPANION_AGGRESSIVE, ))),
        (u'PEACEFUL', 5, u'миролюбивый', u'понижает агрессивность героя', True,
         ChangeHabits(habit_type=game_relations.HABIT_TYPE.PEACEFULNESS, habit_sources=(heroes_relations.HABIT_CHANGE_SOURCE.COMPANION_PEACEFULL,))),
        (u'RESERVED', 6, u'сдержанный', u'склоняет героя к сдержанности', True,
         ChangeHabits(habit_type=game_relations.HABIT_TYPE.PEACEFULNESS, habit_sources=(heroes_relations.HABIT_CHANGE_SOURCE.COMPANION_PEACEFULL_NEUTRAL_1,
                                                                                        heroes_relations.HABIT_CHANGE_SOURCE.COMPANION_PEACEFULL_NEUTRAL_2))),
        (u'CANNY', 7, u'себе на уме', u'склоняет героя быть себе на уме', True,
         ChangeHabits(habit_type=game_relations.HABIT_TYPE.HONOR, habit_sources=(heroes_relations.HABIT_CHANGE_SOURCE.COMPANION_HONOR_NEUTRAL_1,
                                                                                 heroes_relations.HABIT_CHANGE_SOURCE.COMPANION_HONOR_NEUTRAL_2))),
        (u'HONEST', 8, u'честный', u'повышает честь героя', True,
         ChangeHabits(habit_type=game_relations.HABIT_TYPE.HONOR, habit_sources=(heroes_relations.HABIT_CHANGE_SOURCE.COMPANION_HONORABLE,))),
        (u'SNEAKY', 9, u'подлый', u'понижает честь героя', True,
         ChangeHabits(habit_type=game_relations.HABIT_TYPE.HONOR, habit_sources=(heroes_relations.HABIT_CHANGE_SOURCE.COMPANION_DISHONORABLE,))),

        (u'CHARMING', 10, u'очаровательный', u'симпатичен горожанам. Крупный бонус к денежной награде за квесты', True, QuestMoneyReward(multiplier=2.0)),
        (u'CUTE', 11, u'милый', u'симпатичен горожанам. Небольшой бонус к денежной награде за квесты', True, QuestMoneyReward(multiplier=1.5)),
        (u'FRIGHTFUL', 12, u'страшный', u'пугает горожан своим видом. Маленький штраф к оплате квестов.', True, QuestMoneyReward(multiplier=0.75)),
        (u'TERRIBLE', 13, u'мороз по коже', u'пугает горожан своим видом. Болшой штраф к оплате квестов.', True, QuestMoneyReward(multiplier=0.50)),

        (u'PACK', 14, u'вьючный', u'1 дополнительное место для лута', False, MaxBagSize(summand=1)),
        (u'FREIGHT', 15, u'грузовой', u'2 дополнительных места для лута', False, MaxBagSize(summand=2)),
        (u'DRAFT', 16, u'тягловой', u'3 дополнительных места для лута', False, MaxBagSize(summand=3)),

        (u'KNOWN', 17, u'известный', u'находит более политически важную работу', False, PoliticsPower(multiplier=1.5)),
        (u'CAD', 18, u'хам', u'хамит горожанам. Минус к влиянию заданий', True, PoliticsPower(multiplier=0.75)),

        (u'FIT_OF_ENERGY', 19, u'прилив сил', u'бонус к физическому урону, наносимому героем', False, MagicDamageBonus(multiplier=1.1)),
        (u'PEP', 20, u'бодрость духа', u'бонус к магическому урону, наносимому героем', False, PhysicDamageBonus(multiplier=1.1)),

        (u'SLED', 21, u'ездовой', u'постоянный небольшой бонус к скорости героя', False, Speed(multiplier=1.1)),
        (u'SLOW', 22, u'медлительный', u'постоянный штраф к скорости героя', True, Speed(multiplier=0.8)),
        (u'FOOTED_SLED', 23, u'быстроногий ездовой', u'постоянный бонус к скорости героя', False, Speed(multiplier=1.2)),

        (u'FIGHTER', 24, u'боец', u'увеличивает инициативу героя, в бою может применить способность «Удар»', False, BattleAbilityHit()),
        (u'RAM', 25, u'громила', u'увеличивает инициативу героя, в бою может применить способность «Тяжёлый удар»', False, BattleAbilityStrongHit()),
        (u'HOUSEBREAKER', 26, u'таран', u'увеличивает инициативу героя, в бою может применить способность «Разбег-толчок»', False, BattleAbilityRunUpPush()),
        (u'ARSONIST', 27, u'поджигатель', u'увеличивает инициативу героя, в бою может применить способность «Огненный шар»', False, BattleAbilityFireball()),
        (u'POISONER', 28, u'отравитель', u'увеличивает инициативу героя, в бою может применить способность «Ядовитое облако»', False, BattleAbilityPoisonCloud()),
        (u'FROST', 29, u'морозко', u'увеличивает инициативу героя, в бою может применить способность «Заморозка»', False, BattleAbilityFreezing()),


        (u'UNGAINLY', 30, u'неуклюжий', u'большой штраф к инициативе героя', True, Initiative(multiplier=0.8)),
        (u'CLUMSY', 31, u'неповоротливый', u'малый штраф к инициативе героя', True, Initiative(multiplier=0.9)),
        (u'CLEVER', 32, u'ловкий', u'малый бонус к инициативе героя', True, Initiative(multiplier=1.1)),
        (u'IMPETUOUS', 33, u'стремительный', u'большой бонус к инициативе героя', True, Initiative(multiplier=1.2)),

        (u'NOISY', 34, u'шумный', u'так сильно шумит, что привлекает внимание большего количесва врагов', True, BattleProbability(summand=0.05)),
        (u'DEATHY', 35, u'смертельно страшный', u'распугивает чудищ, вероятность встретить врага стремится к нулю', True, BattleProbability(summand=-1)),

        (u'SHARP_EYE', 36, u'зоркий глаз', u'издали высматривает врагов, снижая вероятность встречи с ними', True, BattleProbability(summand=0.05)),

        (u'TORTURER', 37, u'терзатель', u'растерзывает врагов в бою так сильно, что уменьшается шанс найти уцелевший лут с мобов', True, LootProbability(multiplier=0.8)),
        (u'HUNTER', 38, u'охотник', u'увеличивает шанс поднятия лута со всех врагов', False, LootProbability(multiplier=1.2)),

        (u'NOT_LIFER', 39, u'тщедушный', u'получает дополнительную едину урона', True, CompanionDamage(summand=1)),
        (u'PUNY', 40, u'не жилец', u'получает дополнительные 2 единицы урона', True, CompanionDamage(summand=2)),

        (u'CAMOUFLAGE', 41, u'камуфляж', u'реже получает урон в бою', False, CompanionDamageProbability(multiplier=0.9)),
        (u'FLYING', 42, u'летающий', u'значительно реже получает урон в бою', False, CompanionDamageProbability(multiplier=0.8)),

        (u'PICKPOCKET', 43, u'карманник', u'В каждом городе крадёт из карманов горожан немного денег', False, CompanionStealMoney()),
        (u'ROBBER', 44, u'грабитель', u'В каждом городе крадёт у горожан что-нибудь, возможно артефакт', False, CompanionStealItem()),

        (u'COSTLY', 45, u'дорогой', u'при потере спутника герой получает весьма дорогие запчасти, обращаемые в деньги.', False, CompanionSpareParts()),

        (u'WISE', 46, u'мудрый', u'спутник иногда делится мудростью с героем, давая тому немного опыта.', False, CompanionSayWisdom()),
        (u'DIFFICULT', 47, u'сложный', u'герой получает опыт каждый раз, когда ухаживает за спутником', False, CompanionExpPerHeal()),

        (u'FAN', 48, u'поклонник', u'возносит хвалу Хранителю вместе с героем, с небольшой вероятностью даёт бонусную энергию', False, DoubleEnergyRegeneration(summand=0.1)),
        (u'SAN', 49, u'сан', u'возносит хвалу Хранителю вместе с героем, с хорошей вероятностью даёт бонусную энергию', False, DoubleEnergyRegeneration(summand=0.2)),

        (u'EAT_CORPSES', 50, u'пожиратель', u'иногда после боя ест труп врага, пополняя себе хиты. Не ест конструктов, нежить, демонов и стихийных.', False, CompanionEatCorpses()),
        (u'REGENERATE', 51, u'регенерация', u'во время ухода за спутником может восстановить здоровье', False, CompanionRegenerate()),

        (u'EATER', 52, u'едок', u'при каждом посещении города герой тратит деньги на еду для спутника', True, CompanionEat(multiplier=0.25)),
        (u'GLUTTONOUS', 53, u'прожорливый', u'при каждом посещении города герой тратит много денег на еду для спутника', True, CompanionEat(multiplier=0.5)),
        (u'INDEPENDENT', 54, u'самостоятельный', u'может кормиться сам, снижает стоимость кормёжки в 2 раза', False, CompanionEatDiscount(multiplier=0.5)),

        (u'PARAPHERNALIA', 55, u'личные вещи', u'минус 1 место в инвентаре (занятое вещами спутника)', False, MaxBagSize(summand=-1)),
        (u'SPARE_PARTS', 56, u'запчасти', u'минус 2 места в инвентаре (занятые запчастями для спутника)', False, MaxBagSize(summand=-2)),

        (u'DRINKER', 57, u'пьяница', u'спутник пропивает артефакт при посещении героем города', True, CompanionDrinkArtifact()),

        (u'EXORCIST', 58, u'экзорцист', u'спутник изгоняет встречных демонов', False, CompanionExorcist()),

        (u'HEALER', 59, u'лекарь', u'ускоряет лечение героя на отдыхе', False, RestLenght(multiplier=0.5)),

        (u'INSPIRATION', 60, u'воодушевление', u'воодушевляет героя на подвиги, снижая время бездействия между заданиями', False, IDLELenght(multiplier=0.5)),
        (u'LAZY', 61, u'ленивый', u'увеличивает время бездействия между заданиями', True, IDLELenght(multiplier=2.0)),

        (u'COWARDLY', 62, u'трусливый', u'реже защищает героя в бою', False, CompanionBlockProbability(multiplier=0.75)),
        (u'BODYGUARD', 63, u'телохранитель', u'чаще защищает героя в бою', False, CompanionBlockProbability(multiplier=1.25)),

        (u'HUCKSTER', 64, u'торгаш', u'бонус к ценам продажи и покупки', False, Huckster(buy_multiplier=0.8, sell_multiplier=1.2)),

        (u'CONTACT', 65, u'связной', u'увеличивает шанс критической помощи хранителя', False, EtherealMagnet(summand=0.1)),

        (u'TELEPORTATOR', 66, u'телепортатор', u'периодически переносит героя между городами или ключевыми точками задания', False, CompanionTeleport(summand=0.1)),
        (u'FLYER', 67, u'ездовой летун', u'часто  переносит героя на небольшое расстоение по воздуху', False, CompanionFly(summand=0.1)),

        (u'SEDATE', 68, u'степенный', u'постоянный небольшой штраф к скорости героя', True, Speed(multiplier=0.9)),
    )
