# coding: utf-8

from rels import Column
from rels.django import DjangoEnum

from questgen.relations import OPTION_MARKERS as QUEST_OPTION_MARKERS

from the_tale.game.balance import constants as c
from the_tale.game.balance.power import Power, PowerDistribution

from the_tale.game.artifacts.relations import ARTIFACT_TYPE, ARTIFACT_POWER_TYPE


class RISK_LEVEL(DjangoEnum):
    health_percent_to_rest = Column()
    experience_modifier = Column()
    power_modifier = Column()
    reward_modifier = Column()

    records = ( ('VERY_HIGH', 0, u'очень высокий', 0.70, 1.30, 1.30, 1.30),
                 ('HIGH',      1, u'высокий', 0.85, 1.15, 1.15, 1.15),
                 ('NORMAL',    2, u'обычный', 1.00, 1.00, 1.00, 1.00),
                 ('LOW',       3, u'низкий', 1.15, 0.85, 0.85, 0.85),
                 ('VERY_LOW',  4, u'очень низкий', 1.30, 0.70, 0.70, 0.70) )


class ARCHETYPE(DjangoEnum):
    power_distribution = Column()
    description = Column()
    allowed_power_types = Column(no_index=True, unique=False)

    records = ( ('MAGICAL', 0, u'маг', PowerDistribution(0.25, 0.75), u'герой предпочитает магию грубой силе', [ARTIFACT_POWER_TYPE.MOST_MAGICAL,
                                                                                                                ARTIFACT_POWER_TYPE.MAGICAL,
                                                                                                                ARTIFACT_POWER_TYPE.NEUTRAL]),
                ('NEUTRAL', 1, u'авантюрист', PowerDistribution(0.5, 0.5), u'герой соблюдает баланс между мечём и магией', [ARTIFACT_POWER_TYPE.MAGICAL,
                                                                                                                            ARTIFACT_POWER_TYPE.NEUTRAL,
                                                                                                                            ARTIFACT_POWER_TYPE.PHYSICAL]),
                ('PHYSICAL', 2, u'воин', PowerDistribution(0.75, 0.25), u'герой полагается на воинские умения', [ARTIFACT_POWER_TYPE.NEUTRAL,
                                                                                                                 ARTIFACT_POWER_TYPE.PHYSICAL,
                                                                                                                 ARTIFACT_POWER_TYPE.MOST_PHYSICAL]) )


class PREFERENCE_TYPE(DjangoEnum):
    level_required = Column()
    base_name = Column()
    prepair_method = Column(unique=False)
    nullable = Column(unique=False)

    records = ( ('MOB', 0, u'любимая добыча', 53, 'mob', '_prepair_mob', True),
                ('PLACE', 1, u'родной город', 4, 'place', '_prepair_place', True),
                ('FRIEND', 2, u'соратник', 13, 'friend', '_prepair_person', True),
                ('ENEMY', 3, u'противник', 26, 'enemy', '_prepair_person', True),
                ('ENERGY_REGENERATION_TYPE', 4, u'религиозность', 1, 'energy_regeneration_type', '_prepair_value', False),
                ('EQUIPMENT_SLOT', 5, u'экипировка', 43, 'equipment_slot', '_prepair_equipment_slot', True),
                ('RISK_LEVEL', 6, u'уровень риска', 8, 'risk_level', '_prepair_risk_level', False),
                ('FAVORITE_ITEM', 7, u'любимая вещь', 19, 'favorite_item', '_prepair_equipment_slot', True),
                ('ARCHETYPE', 8, u'архетип', 34, 'archetype', '_prepair_archetype', False),
        )


class MONEY_SOURCE(DjangoEnum):

    records = ( ('EARNED_FROM_LOOT', 0, u'заработано продажей добычи'),
                ('EARNED_FROM_ARTIFACTS', 1, u'заработано продажей артефактов'),
                ('EARNED_FROM_QUESTS', 2, u'заработано выполнением квестов'),
                ('EARNED_FROM_HELP', 3, u'получено от хранителя'),
                ('EARNED_FROM_HABITS', 4, u'получено от черт'),

                ('SPEND_FOR_HEAL', 1000, u'потрачено на лечение'),
                ('SPEND_FOR_ARTIFACTS', 1001, u'потрачено на покупку артефактов'),
                ('SPEND_FOR_SHARPENING', 1002, u'потрачено на заточку артефактов'),
                ('SPEND_FOR_USELESS', 1003, u'потрачено без пользы'),
                ('SPEND_FOR_IMPACT', 1004, u'потрачено на изменение влияния'),
                ('SPEND_FOR_EXPERIENCE', 1005, u'потрачено на обучение'),
                ('SPEND_FOR_REPAIRING', 1006, u'потрачено на починку'))



class ITEMS_OF_EXPENDITURE(DjangoEnum):
    ui_id = Column()
    priority = Column(unique=False, primary=False)
    price_fraction = Column(unique=False, primary=False) # цена в доле от стандартной цены
    money_source = Column()
    description = Column()

    records = ( ('INSTANT_HEAL',        0, u'лечение',           'heal',       20, 0.3, MONEY_SOURCE.SPEND_FOR_HEAL,
                  u'Собирает деньги, чтобы поправить здоровье, когда понадобится.'),
                 ('BUYING_ARTIFACT',     1, u'покупка артефакта', 'artifact',   4,  1.5, MONEY_SOURCE.SPEND_FOR_ARTIFACTS,
                  u'Планирует приобретение новой экипировки.'),
                 ('SHARPENING_ARTIFACT', 2, u'заточка артефакта', 'sharpening', 3,  2.0, MONEY_SOURCE.SPEND_FOR_SHARPENING,
                  u'Собирает на улучшение экипировки.'),
                 ('USELESS',             3, u'бесполезные траты', 'useless',    2,  0.4, MONEY_SOURCE.SPEND_FOR_USELESS,
                  u'Копит золото для не очень полезных но безусловно необходимых трат.'),
                 ('IMPACT',              4, u'изменение влияния', 'impact',     4,  2.5, MONEY_SOURCE.SPEND_FOR_IMPACT,
                  u'Планирует накопить деньжат, чтобы повлиять на «запомнившегося» горожанина.'),
                 ('EXPERIENCE',          5, u'обучение',          'experience', 2,  5.0, MONEY_SOURCE.SPEND_FOR_EXPERIENCE,
                  u'Копит деньги в надежде немного повысить свою грамотность.'),
                 ('REPAIRING_ARTIFACT',  6, u'починка артефакта', 'repairing', 3, 1.0, MONEY_SOURCE.SPEND_FOR_REPAIRING,
                  u'Копит на починку экипировки'))


    @classmethod
    def get_quest_upgrade_equipment_fraction(cls):
        return cls.BUYING_ARTIFACT.price_fraction * 0.75




class EQUIPMENT_SLOT(DjangoEnum):
    artifact_type = Column(related_name='equipment_slot')

    records = ( ('HAND_PRIMARY', 0, u'основная рука', ARTIFACT_TYPE.MAIN_HAND),
                 ('HAND_SECONDARY', 1, u'вспомогательная рука', ARTIFACT_TYPE.OFF_HAND),
                 ('HELMET', 2, u'шлем', ARTIFACT_TYPE.HELMET),
                 ('SHOULDERS', 3, u'наплечники', ARTIFACT_TYPE.SHOULDERS),
                 ('PLATE', 4, u'доспех', ARTIFACT_TYPE.PLATE),
                 ('GLOVES', 5, u'перчатки', ARTIFACT_TYPE.GLOVES),
                 ('CLOAK', 6, u'плащ', ARTIFACT_TYPE.CLOAK),
                 ('PANTS', 7, u'штаны', ARTIFACT_TYPE.PANTS),
                 ('BOOTS', 8, u'сапоги', ARTIFACT_TYPE.BOOTS),
                 ('AMULET', 9, u'амулет', ARTIFACT_TYPE.AMULET),
                 ('RING', 10, u'кольцо', ARTIFACT_TYPE.RING) )


class MODIFIERS(DjangoEnum):
    default = Column(unique=False, single_type=False)

    records = ( ('INITIATIVE', 0, u'инициатива', lambda: 1.0),
                ('HEALTH', 1, u'здоровье', lambda: 1.0),
                ('DAMAGE', 2, u'урон', lambda: 1.0),
                ('SPEED', 3, u'скорость', lambda: 1.0),
                ('MIGHT_CRIT_CHANCE', 4, u'шанс критического срабатвания способности Хранителя', lambda: 0.0),
                ('EXPERIENCE', 5, u'опыт', lambda: 1.0),
                ('MAX_BAG_SIZE', 6, u'максимальный размер рюкзака', lambda: 0),
                ('POWER', 7, u'влияние героя', lambda: 1.0),
                ('QUEST_MONEY_REWARD', 8, u'денежная награда за выполнение задения', lambda: 1.0),
                ('BUY_PRICE', 9, u'цена покупки', lambda: 1.0),
                ('SELL_PRICE', 10, u'цена продажи', lambda: 1.0),
                ('ITEMS_OF_EXPENDITURE_PRIORITIES', 11, u'приортет трат', lambda: {record:record.priority for record in ITEMS_OF_EXPENDITURE.records}),
                ('GET_ARTIFACT_FOR_QUEST', 12, u'получить артефакты за задания', lambda: c.ARTIFACT_FOR_QUEST_PROBABILITY),
                ('BUY_BETTER_ARTIFACT', 13, u'купить лучший артефакт', lambda: 0),
                ('KILL_BEFORE_BATTLE', 14, u'убить монстра перед боем', lambda: False),
                ('PICKED_UP_IN_ROAD', 15, u'ехать на попутных телегах', lambda: False),
                ('POWER_TO_FRIEND', 16, u'бонус к влиянию на друга', lambda: 1.0),
                ('POWER_TO_ENEMY', 17, u'бонус к влиянию на врага', lambda: 1.0),
                ('QUEST_MARKERS', 18, u'маркеры задания', lambda: {}),
                ('QUEST_MARKERS_REWARD_BONUS', 19, u'бонус наград за правильный выбор', lambda: {}),
                ('LOOT_PROBABILITY', 21, u'вероятность получить лут после боя', lambda: 1.0),
                ('EXP_FOR_KILL', 22, u'опыт за убийство моснтра', lambda: 1.0),
                ('PEACEFULL_BATTLE', 23, u'мирный бой', lambda: False),
                ('FRIEND_QUEST_PRIORITY', 24, u'приоритет задания на помощь другу', lambda: 1.0),
                ('ENEMY_QUEST_PRIORITY', 25, u'приоритет задания на вредительство врагу', lambda: 1.0),
                ('HONOR_EVENTS', 26, u'события для черт', lambda: set()),
                ('SAFE_ARTIFACT_INTEGRITY', 27, u'сохранить целостность артефакта', lambda: 0),
                ('MAGIC_DAMAGE', 28, u'бонус к магическому урону', lambda: 1.0),
                ('PHYSIC_DAMAGE', 29, u'бонус к физическому урону', lambda: 1.0),
                ('MAX_ENERGY', 30, u'бонус к максимуму энергии', lambda: 0),
                ('REST_LENGTH', 31, u'длительность отдыха', lambda: 1.0),
                ('RESURRECT_LENGTH', 32, u'длительность воскрешения', lambda: 1.0),
                ('IDLE_LENGTH', 33, u'длительность бездействия', lambda: 1.0),
                ('ENERGY_DISCOUNT', 34, u'скидка на трату энергии', lambda: 0),
                ('DOUBLE_ENERGY_REGENERATION', 35, u'вероятность восстановить в 2 раза больше энергии', lambda: 0),
                ('BONUS_ARTIFACT_POWER', 36, u'бонус к силе артефактов получаемых', lambda: Power(0, 0)),
                ('ADDITIONAL_ABILITIES', 37, u'дополнительные способности', lambda: []),
                ('PREFERENCES_CHANCE_DELAY', 38, u'зедержка смены предпочтений', lambda: c.PREFERENCES_CHANGE_DELAY),
                ('FEAR', 39, u'монстры могу убежать в начале боя', lambda: 0),
                ('CLOUDED_MIND', 40, u'поступки героя перестают зависеть от черт', lambda: False),
                ('RARE', 41, u'увеличиена вероятность получить редкий артефакт', lambda: 1),
                ('EPIC', 42, u'увеличиена вероятность получить эпический артефакт', lambda: 1),
                ('HABITS_INCREASE', 43, u'скорость роста черт', lambda: 1),
                ('HABITS_DECREASE', 44, u'скорость уменьшения черт', lambda: 1),
                ('SAFE_INTEGRITY', 45, u'вероятность сохранить целостность артефакта после боя', lambda: 0))



class HABIT_INTERVAL(DjangoEnum):
    female_text = Column()
    neuter_text = Column()
    left_border = Column()
    right_border = Column()


class HABIT_HONOR_INTERVAL(HABIT_INTERVAL):

    records = ( ('LEFT_3', 0, u'бесчестный', u'бесчестная', u'бесчестное', -c.HABITS_BORDER, c.HABITS_RIGHT_BORDERS[0]),
                ('LEFT_2', 1, u'подлый', u'подлая', u'подлое', c.HABITS_RIGHT_BORDERS[0], c.HABITS_RIGHT_BORDERS[1]),
                ('LEFT_1', 2, u'порочный', u'порочная', u'порочное', c.HABITS_RIGHT_BORDERS[1], c.HABITS_RIGHT_BORDERS[2]),
                ('NEUTRAL', 3, u'себе на уме', u'себе на уме', u'себе на уме', c.HABITS_RIGHT_BORDERS[2], c.HABITS_RIGHT_BORDERS[3]),
                ('RIGHT_1', 4, u'порядочный', u'порядочная', u'порядочное', c.HABITS_RIGHT_BORDERS[3], c.HABITS_RIGHT_BORDERS[4]),
                ('RIGHT_2', 5, u'благородный', u'благородная', u'благородное', c.HABITS_RIGHT_BORDERS[4], c.HABITS_RIGHT_BORDERS[5]),
                ('RIGHT_3', 6, u'хозяин своего слова', u'хозяйка своего слова', u'хозяин своего слова', c.HABITS_RIGHT_BORDERS[5], c.HABITS_BORDER) )


class HABIT_PEACEFULNESS_INTERVAL(HABIT_INTERVAL):
    records = ( ('LEFT_3', 0, u'скорый на расправу', u'скорая на расправу', u'скорое на расправу', -c.HABITS_BORDER, c.HABITS_RIGHT_BORDERS[0]),
                ('LEFT_2', 1, u'вспыльчивый', u'вспыльчивая', u'вспыльчивое', c.HABITS_RIGHT_BORDERS[0], c.HABITS_RIGHT_BORDERS[1]),
                ('LEFT_1', 2, u'задира', u'задира', u'задира', c.HABITS_RIGHT_BORDERS[1], c.HABITS_RIGHT_BORDERS[2]),
                ('NEUTRAL', 3, u'сдержанный', u'сдержанная', u'сдержаное', c.HABITS_RIGHT_BORDERS[2], c.HABITS_RIGHT_BORDERS[3]),
                ('RIGHT_1', 4, u'доброхот', u'доброхот', u'доброхот', c.HABITS_RIGHT_BORDERS[3], c.HABITS_RIGHT_BORDERS[4]),
                ('RIGHT_2', 5, u'миролюбивый', u'миролюбивая', u'миролюбивое', c.HABITS_RIGHT_BORDERS[4], c.HABITS_RIGHT_BORDERS[5]),
                ('RIGHT_3', 6, u'гуманист', u'гуманист', u'гуманист', c.HABITS_RIGHT_BORDERS[5], c.HABITS_BORDER) )


class HABIT_CHANGE_SOURCE(DjangoEnum):
    quest_marker = Column(unique=False, single_type=False)
    quest_default = Column(unique=False, single_type=False)
    correlation_requirements = Column(unique=False, single_type=False)
    honor = Column(unique=False)
    peacefulness = Column(unique=False)

    records = ( ('QUEST_HONORABLE', 0, u'выбор чести в задании игроком', QUEST_OPTION_MARKERS.HONORABLE, False, None,           c.HABITS_QUEST_ACTIVE_DELTA, 0.0),
                ('QUEST_DISHONORABLE', 1, u'выбор бесчестия в задании игроком', QUEST_OPTION_MARKERS.DISHONORABLE, False, None,  -c.HABITS_QUEST_ACTIVE_DELTA, 0.0),
                ('QUEST_AGGRESSIVE', 2, u'выборе агрессивности в задании игроком', QUEST_OPTION_MARKERS.AGGRESSIVE, False, None, 0.0, -c.HABITS_QUEST_ACTIVE_DELTA),
                ('QUEST_UNAGGRESSIVE', 3, u'выбор миролюбия в задании игроком', QUEST_OPTION_MARKERS.UNAGGRESSIVE, False, None,  0.0, c.HABITS_QUEST_ACTIVE_DELTA),

                ('QUEST_HONORABLE_DEFAULT', 4, u'выбор чести в задании героем', QUEST_OPTION_MARKERS.HONORABLE, True, False,            c.HABITS_QUEST_PASSIVE_DELTA, 0.0),
                ('QUEST_DISHONORABLE_DEFAULT', 5, u'выбор бесчестия в задании героем', QUEST_OPTION_MARKERS.DISHONORABLE, True, False,  -c.HABITS_QUEST_PASSIVE_DELTA, 0.0),
                ('QUEST_AGGRESSIVE_DEFAULT', 6, u'выборе агрессивности в задании героем', QUEST_OPTION_MARKERS.AGGRESSIVE, True, False, 0.0, -c.HABITS_QUEST_PASSIVE_DELTA),
                ('QUEST_UNAGGRESSIVE_DEFAULT', 7, u'выбор миролюбия в задании героем', QUEST_OPTION_MARKERS.UNAGGRESSIVE, True, False,  0.0, c.HABITS_QUEST_PASSIVE_DELTA),

                ('HELP_AGGRESSIVE', 8, u'помощь в бою', None, None, None,       0.0, -c.HABITS_HELP_ABILITY_DELTA),
                ('HELP_UNAGGRESSIVE', 9, u'помощь вне боя', None, None, None,   0.0, c.HABITS_HELP_ABILITY_DELTA),
                ('ARENA_SEND', 10, u'отправка на арену', None, None, None,      0.0, -c.HABITS_ARENA_ABILITY_DELTA),
                ('ARENA_LEAVE', 11, u'покидание арены', None, None, None,       0.0, c.HABITS_ARENA_ABILITY_DELTA),

                ('PERIODIC_LEFT', 12, u'периодическое изменение (слева)', None, None, False, c.HABITS_PERIODIC_DELTA, c.HABITS_PERIODIC_DELTA),
                ('PERIODIC_RIGHT', 13, u'периодическое изменение (справа)', None, None, False, -c.HABITS_PERIODIC_DELTA, -c.HABITS_PERIODIC_DELTA) )


class HABIT_TYPE(DjangoEnum):
    intervals = Column()

    records = ( ('HONOR', 0, u'честь', HABIT_HONOR_INTERVAL),
                ('PEACEFULNESS', 1, u'миролюбие', HABIT_PEACEFULNESS_INTERVAL) )
