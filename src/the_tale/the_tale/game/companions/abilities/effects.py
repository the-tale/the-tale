
import smart_imports

smart_imports.all()


class Base(object):
    TYPE = NotImplemented

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


class QuestMoneyReward(Summand):
    TYPE = relations.EFFECT.QUEST_MONEY_REWARD
    MODIFIER = heroes_relations.MODIFIERS.QUEST_MONEY_REWARD


class MaxBagSize(Summand):
    TYPE = relations.EFFECT.MAX_BAG_SIZE
    MODIFIER = heroes_relations.MODIFIERS.MAX_BAG_SIZE


class PoliticsPower(Summand):
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
    ABILITY = NotImplemented

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
    ABILITY = heroes_abilities_battle.HIT(1)


class BattleAbilityStrongHit(BaseBattleAbility):
    TYPE = relations.EFFECT.BATTLE_ABILITY_STRONG_HIT
    ABILITY = heroes_abilities_battle.STRONG_HIT(5)


class BattleAbilityRunUpPush(BaseBattleAbility):
    TYPE = relations.EFFECT.BATTLE_ABILITY_RUN_UP_PUSH
    ABILITY = heroes_abilities_battle.RUN_UP_PUSH(5)


class BattleAbilityFireball(BaseBattleAbility):
    TYPE = relations.EFFECT.BATTLE_ABILITY_FIREBALL
    ABILITY = heroes_abilities_battle.FIREBALL(5)


class BattleAbilityPoisonCloud(BaseBattleAbility):
    TYPE = relations.EFFECT.BATTLE_ABILITY_POSION_CLOUD
    ABILITY = heroes_abilities_battle.POISON_CLOUD(5)


class BattleAbilityFreezing(BaseBattleAbility):
    TYPE = relations.EFFECT.BATTLE_ABILITY_FREEZING
    ABILITY = heroes_abilities_battle.FREEZING(5)


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


class Huckster(Summand):
    TYPE = relations.EFFECT.HUCKSTER

    def __init__(self, buy_bonus_left, buy_bonus_right, sell_bonus_left, sell_bonus_right):
        super(Huckster, self).__init__(summand_left=None)
        self.buy_bonus_left = buy_bonus_left
        self.buy_bonus_right = buy_bonus_right
        self.sell_bonus_left = sell_bonus_left
        self.sell_bonus_right = sell_bonus_right

    def _modify_attribute(self, abilities_levels, modifier, value):
        if modifier.is_BUY_PRICE:
            return value + aprox(self.buy_bonus_left,
                                 self.buy_bonus_right,
                                 abilities_levels.get(self.TYPE.metatype, 0))

        if modifier.is_SELL_PRICE:
            # +1 for increase price on low levels
            return value + aprox(self.sell_bonus_left,
                                 self.sell_bonus_right,
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

# abilities constructors


def quest_money_reward(name, value, text, description, rarity_delta, border_left, border_right, work_when_dead=False, can_be_freezed=True):
    QUEST_MONEY_REWARD_BORDERS = [0.5, 1.0, 2.0]

    if border_left < border_right:
        description = (description + ' (от +%d%% до +%d%%)') % (QUEST_MONEY_REWARD_BORDERS[border_left] * 100, QUEST_MONEY_REWARD_BORDERS[border_right] * 100)
        effect = QuestMoneyReward(QUEST_MONEY_REWARD_BORDERS[border_left], QUEST_MONEY_REWARD_BORDERS[border_right])
    else:
        description = (description + ' (от -%d%% до -%d%%)') % (QUEST_MONEY_REWARD_BORDERS[border_left] * 100, QUEST_MONEY_REWARD_BORDERS[border_right] * 100)
        effect = QuestMoneyReward(-QUEST_MONEY_REWARD_BORDERS[border_left], -QUEST_MONEY_REWARD_BORDERS[border_right])

    return (name,
            value,
            text,
            description,
            effect,
            rarity_delta,
            work_when_dead,
            can_be_freezed)


def huckster(name, value, text, description, rarity_delta, work_when_dead=False, can_be_freezed=True):
    effect = Huckster(buy_bonus_left=heroes_abilities_nonbattle.HUCKSTER.BUY_BONUS[-1] / 2 / 5, buy_bonus_right=heroes_abilities_nonbattle.HUCKSTER.BUY_BONUS[-1] / 2,
                      sell_bonus_left=heroes_abilities_nonbattle.HUCKSTER._sell_bonus(5) / 2 / 5, sell_bonus_right=heroes_abilities_nonbattle.HUCKSTER._sell_bonus(5) / 2)
    return (name,
            value,
            text,
            (description + '(покупка от %.2f%% до %.2f%%; продажа от +%.2f%% до +%.2f%%)') % (effect.buy_bonus_left * 100, effect.buy_bonus_right * 100, effect.sell_bonus_left * 100, effect.sell_bonus_right * 100),
            effect,
            rarity_delta,
            work_when_dead,
            can_be_freezed)


class ABILITIES(rels_django.DjangoEnum):
    description = rels.Column()
    effect = rels.Column(single_type=False)
    rarity_delta = rels.Column(unique=False)
    work_when_dead = rels.Column(unique=False)
    can_be_freezed = rels.Column(unique=False)

    records = (
        ('OBSTINATE', 0, 'строптивый', 'слаженность растёт очень медленно', CoherenceSpeed(0.6), RARITY_LOWER, False, True),
        ('STUBBORN', 1, 'упрямый', 'слаженность растёт медленнее обычного', CoherenceSpeed(0.8), RARITY_LOW, False, True),
        ('BONA_FIDE', 2, 'добросовестный', 'слаженность растёт быстрее обычного', CoherenceSpeed(1.2), RARITY_BIG, False, True),
        ('MANAGING', 3, 'исполнительный', 'слаженность растёт очень быстро', CoherenceSpeed(1.40), RARITY_BIGER, False, True),

        ('AGGRESSIVE', 4, 'агрессивный', 'увеличивает агрессивность героя',
         ChangeHabits(habit_type=game_relations.HABIT_TYPE.PEACEFULNESS, habit_sources=(heroes_relations.HABIT_CHANGE_SOURCE.COMPANION_AGGRESSIVE, )), RARITY_NEUTRAL, False, True),
        ('PEACEFUL', 5, 'миролюбивый', 'увеличивает миролюбие героя',
         ChangeHabits(habit_type=game_relations.HABIT_TYPE.PEACEFULNESS, habit_sources=(heroes_relations.HABIT_CHANGE_SOURCE.COMPANION_PEACEFULL,)), RARITY_NEUTRAL, False, True),
        ('RESERVED', 6, 'сдержанный', 'склоняет героя к балансу между агрессивностью и миролюбием',
         ChangeHabits(habit_type=game_relations.HABIT_TYPE.PEACEFULNESS, habit_sources=(heroes_relations.HABIT_CHANGE_SOURCE.COMPANION_PEACEFULL_NEUTRAL_1,
                                                                                        heroes_relations.HABIT_CHANGE_SOURCE.COMPANION_PEACEFULL_NEUTRAL_2)), RARITY_NEUTRAL, False, True),
        ('CANNY', 7, 'себе на уме', 'склоняет героя к балансу между честью и бесчестием',
         ChangeHabits(habit_type=game_relations.HABIT_TYPE.HONOR, habit_sources=(heroes_relations.HABIT_CHANGE_SOURCE.COMPANION_HONOR_NEUTRAL_1,
                                                                                 heroes_relations.HABIT_CHANGE_SOURCE.COMPANION_HONOR_NEUTRAL_2)), RARITY_NEUTRAL, False, True),
        ('HONEST', 8, 'честный', 'увеличивает честь героя',
         ChangeHabits(habit_type=game_relations.HABIT_TYPE.HONOR, habit_sources=(heroes_relations.HABIT_CHANGE_SOURCE.COMPANION_HONORABLE,)), RARITY_NEUTRAL, False, True),
        ('SNEAKY', 9, 'подлый', 'уменьшает честь героя',
         ChangeHabits(habit_type=game_relations.HABIT_TYPE.HONOR, habit_sources=(heroes_relations.HABIT_CHANGE_SOURCE.COMPANION_DISHONORABLE,)), RARITY_NEUTRAL, False, True),

        quest_money_reward('CHARMING', 10, 'очаровательный', 'очень симпатичен горожанам, герой получает крупный бонус к награде за задания', RARITY_BIGER, 1, 2),
        quest_money_reward('CUTE', 11, 'милый', 'симпатичен горожанам, герой получает небольшой бонус к награде за задания', RARITY_BIG, 0, 1),
        quest_money_reward('FRIGHTFUL', 12, 'страшный', 'пугает горожан, герой получает меньшие награды за задания', RARITY_LOW, 1, 0),
        quest_money_reward('TERRIBLE', 13, 'мороз по коже', 'сильно пугает горожан, герой получает значительно меньшие награды за задание', RARITY_LOWER, 2, 1),

        ('PACK', 14, 'вьючный', '2 дополнительных места в рюкзаке', MaxBagSize(2), RARITY_BIG, False, True),
        ('FREIGHT', 15, 'грузовой', '4 дополнительных места в рюкзаке', MaxBagSize(4), RARITY_BIGER, False, True),
        ('DRAFT', 16, 'тягловой', '6 дополнительных мест в рюкзаке', MaxBagSize(6), RARITY_BIGEST, False, True),

        ('PARAPHERNALIA', 55, 'личные вещи', 'забирает 2 места в рюкзаке для своих вещей', MaxBagSize(-2), RARITY_LOW, False, True),
        ('SPARE_PARTS', 56, 'запчасти', 'забирает 4 места в рюкзаке для запчастей', MaxBagSize(-4), RARITY_LOWER, False, True),

        ('KNOWN', 17, 'известный', 'находит политически важную работу, задания героя оказывают большее влияние на мир (максимальный бонус к влиянию: 100%)',
         PoliticsPower(0.5, 1.0), RARITY_BIGER, False, True),
        ('CAD', 18, 'хам', 'хамит горожанам, герою не доверяют политически важную работу, поэтому он оказывает меньшее влияние на мир (минимальный штраф к влиянию: -50%)',
         PoliticsPower(-1.0, -0.5), RARITY_LOWER, False, True),

        ('FIT_OF_ENERGY', 19, 'прилив сил', 'даёт небольшой бонус к физическому урону героя', PhysicDamageBonus(1.05, 1.1), RARITY_BIGER, False, True),
        ('PEP', 20, 'бодрость духа', 'даёт небольшой бонус к магическому урону героя', MagicDamageBonus(1.05, 1.1), RARITY_BIGER, False, True),

        ('SLOW', 22, 'медлительный', 'постоянный штраф к скорости героя', Speed(0.7, 0.85), RARITY_LOWER, False, True),
        ('SEDATE', 68, 'степенный', 'постоянный небольшой штраф к скорости героя', Speed(0.8, 0.9), RARITY_LOW, False, True),
        ('SLED', 21, 'ездовой', 'постоянный небольшой бонус к скорости героя', Speed(1.05, 1.10), RARITY_BIG, False, True),
        ('RACER', 23, 'скакун', 'постоянный бонус к скорости героя', Speed(1.1, 1.15), RARITY_BIGER, False, True),
        ('FLEET_FOOTED', 69, 'быстроногий', 'постоянный большой бонус к скорости героя', Speed(1.1, 1.2), RARITY_BIGEST, False, True),

        ('FIGHTER', 24, 'боец', 'немного увеличивает инициативу героя, в бою может применить способность «%s»' % BattleAbilityHit.ABILITY.NAME, BattleAbilityHit(), RARITY_BIGER, False, True),
        ('RAM', 25, 'громила', 'немного увеличивает инициативу героя, в бою может применить способность «%s»' % BattleAbilityStrongHit.ABILITY.NAME, BattleAbilityStrongHit(), RARITY_BIGER, False, True),
        ('HOUSEBREAKER', 26, 'таран', 'немного увеличивает инициативу героя, в бою может применить способность «%s»' % BattleAbilityRunUpPush.ABILITY.NAME, BattleAbilityRunUpPush(), RARITY_BIGER, False, True),
        ('ARSONIST', 27, 'поджигатель', 'немного увеличивает инициативу героя, в бою может применить способность «%s»' % BattleAbilityFireball.ABILITY.NAME, BattleAbilityFireball(), RARITY_BIGER, False, True),
        ('POISONER', 28, 'отравитель', 'немного увеличивает инициативу героя, в бою может применить способность «%s»' % BattleAbilityPoisonCloud.ABILITY.NAME, BattleAbilityPoisonCloud(), RARITY_BIGER, False, True),
        ('FROST', 29, 'морозко', 'немного увеличивает инициативу героя, в бою может применить способность «%s»' % BattleAbilityFreezing.ABILITY.NAME, BattleAbilityFreezing(), RARITY_BIGER, False, True),

        ('UNGAINLY', 30, 'неуклюжий', 'большой штраф к инициативе героя', Initiative(0.8, 0.875), RARITY_LOWER, False, True),
        ('CLUMSY', 31, 'неповоротливый', 'малый штраф к инициативе героя', Initiative(0.89, 0.94), RARITY_LOW, False, True),
        ('CLEVER', 32, 'ловкий', 'малый бонус к инициативе героя', Initiative(1.01, 1.06), RARITY_BIGER, False, True),
        ('IMPETUOUS', 33, 'стремительный', 'большой бонус к инициативе героя', Initiative(1.05, 1.125), RARITY_BIGER, False, True),

        ('NOISY', 34, 'шумный', 'так сильно шумит, что привлекает внимание большего количества врагов', BattleProbability(0.2, 0.1), RARITY_LOWER, False, True),
        ('SHARP_EYE', 36, 'острый глаз', 'издали высматривает врагов, снижая вероятность встречи с ними', BattleProbability(-0.05, -0.1), RARITY_BIGER, False, True),

        ('DEATHY', 35, 'смертельно страшный', 'распугивает всех, кого встречает, вероятность встретить врага стремится к нулю', Deathy(-1), RARITY_BIGEST, False, True),

        ('TORTURER', 37, 'терзатель', 'растерзывает врагов в бою так сильно, что уменьшается шанс найти уцелевшую в бою добычу', LootProbability(0.6, 0.8), RARITY_LOWER, False, True),
        ('HUNTER', 38, 'охотник', 'помогает герою сражаться аккуратнее, благодаря чему увеличивает шанс найти уцелевшую в бою добычу', LootProbability(1.1, 1.2), RARITY_BIGER, False, True),

        ('NOT_LIFER', 39, 'тщедушный', 'при ранении может получить дополнительный урон', CompanionDamage(c.COMPANIONS_DAMAGE_PER_WOUND), RARITY_LOWER, False, True),
        ('PUNY', 40, 'не жилец', 'при ранении может получить большой дополнительный урон', CompanionDamage(2 * c.COMPANIONS_DAMAGE_PER_WOUND), RARITY_LOWEST, False, True),

        ('CAMOUFLAGE', 41, 'камуфляж', 'благодаря незаметности, реже получает урон в бою', CompanionDamageProbability(0.9, 0.8), RARITY_BIGER, False, True),
        ('FLYING', 42, 'летающий', 'перемещаясь не только вокруг но и над противником, значительно реже получает урон в бою', CompanionDamageProbability(0.85, 0.7), RARITY_BIGEST, False, True),

        ('PICKPOCKET', 43, 'карманник', 'В каждом городе крадёт из карманов горожан немного денег', CompanionStealMoney(0.5, 3.0), RARITY_BIG, False, True),
        ('ROBBER', 44, 'грабитель', 'В каждом городе крадёт у горожан что-нибудь полезное, возможно, даже экипировку', CompanionStealItem(1.05, 4.0), RARITY_BIGER, False, True),

        ('COSTLY', 45, 'дорогой', 'при потере спутника герой получает весьма дорогие запчасти, обращаемые в деньги.', CompanionSpareParts(), RARITY_BIG, False, True),

        ('WISE', 46, 'мудрый', 'спутник иногда делится мудростью с героем, давая тому немного опыта.', CompanionSayWisdom(0.5, 1.0), RARITY_BIGER, False, True),
        ('DIFFICULT', 47, 'сложный', 'ухаживая за спутником, герой может получить немного опыта', CompanionExpPerHeal(0.5, 1.0), RARITY_BIGER, False, True),

        ('FAN', 48, 'поклонник', 'возносит хвалу Хранителю вместе с героем и с небольшой вероятностью даёт бонусную энергию', DoubleEnergyRegeneration(0.05, 0.1), RARITY_BIGER, False, True),
        ('SAN', 49, 'сан', 'возносит хвалу Хранителю вместе с героем и с хорошей вероятностью даёт бонусную энергию', DoubleEnergyRegeneration(0.1, 0.2), RARITY_BIGEST, False, True),

        ('EAT_CORPSES', 50, 'пожиратель', 'после боя иногда ест труп врага, пополняя себе здоровье. Не ест конструктов, нежить, демонов и стихийных существ.', CompanionEatCorpses(0.5, 1), RARITY_BIGER, False, True),
        ('REGENERATE', 51, 'регенерация', 'во время отдыха может восстановить своё здоровье', CompanionRegenerate(0.5, 1.0), RARITY_BIGER, False, True),

        ('EATER', 52, 'едок', 'при каждом посещении города герой тратит деньги на еду для спутника', CompanionEat(0.35, 0.25), RARITY_LOW, False, True),
        ('GLUTTONOUS', 53, 'прожорливый', 'при каждом посещении города герой тратит много денег на еду для спутника', CompanionEat(0.7, 0.5), RARITY_LOWER, False, True),
        ('INDEPENDENT', 54, 'самостоятельный', 'может кормиться сам, снижает стоимость кормёжки (способностей «едок» и «прожорливый»)', CompanionEatDiscount(0.9, 0.5), RARITY_BIG, False, True),

        ('DRINKER', 57, 'пьяница', 'спутник пропивает случайный предмет из рюкзака при посещении героем города', CompanionDrinkArtifact(0.95, 0.5), RARITY_BIG, False, True),

        ('EXORCIST', 58, 'экзорцист', 'спутник может изгнать встречного демона или стихийное существо', CompanionExorcist(0.5, 1.0), RARITY_BIG, False, True),

        ('HEALER', 59, 'лекарь', 'ускоряет лечение героя на отдыхе', RestLenght(0.9, 0.5), RARITY_BIGEST, False, True),

        ('INSPIRATION', 60, 'воодушевление', 'воодушевляет героя на подвиги, снижая время бездействия между заданиями', IDLELenght(0.9, 0.5), RARITY_BIG, False, True),
        ('LAZY', 61, 'ленивый', 'ленится вместе с героем и увеличивает время бездействия между заданиями', IDLELenght(2.0, 1.5), RARITY_LOW, False, True),

        ('COWARDLY', 62, 'трусливый', 'реже защищает героя в бою', CompanionBlockProbability(0.5, 0.75), RARITY_NEUTRAL, False, True),
        ('BODYGUARD', 63, 'телохранитель', 'чаще защищает героя в бою', CompanionBlockProbability(1.1, 1.25), RARITY_NEUTRAL, False, True),

        # TODO: increase rarity?
        huckster('HUCKSTER', 64, 'торгаш', 'помогает герою торговаться, увеличивая цены продажи и уменьшая цены покупки', RARITY_BIG),

        ('CONTACT', 65, 'связной', 'служит маяком для Хранителя и увеличивает шанс критической помощи', EtherealMagnet(0.05, 0.1), RARITY_BIGEST, False, True),

        ('TELEPORTATOR', 66, 'телепортатор', 'периодически переносит героя между городами или ключевыми точками задания', CompanionTeleport(0.05, 0.1), RARITY_BIGEST, False, True),
        ('FLYER', 67, 'ездовой летун', 'часто  переносит героя на небольшое расстояние по воздуху', CompanionFly(0.05, 0.1), RARITY_BIGEST, False, True),

        ('UNCOMMON', 70, 'редкий', 'спутник встречается реже обычного', Rarity(), RARITY_BIGER, False, True),
        ('RARE', 71, 'очень редкий', 'спутник встречается очень редко', Rarity(), RARITY_BIGEST, False, True),
        ('SPECIAL', 72, 'особый', 'особый спутник, которого нельзя получить обычным способом', Rarity(), RARITY_LEGENDARY, False, True),

        ('TEMPORARY', 73, 'временный', 'спутник с небольшой вероятностью может покинуть героя при посещении города и не может быть превращён в карту',
         Unsociable(0.1 * c.COMPANIONS_LEAVE_IN_PLACE), RARITY_LOWEST, True, False),
        ('UNSOCIABLE', 74, 'нелюдимый', 'спутник может покинуть героя при посещении города и не может быть превращён в карту',
         Unsociable(c.COMPANIONS_LEAVE_IN_PLACE), RARITY_LOWEST_2, True, False)
    )
