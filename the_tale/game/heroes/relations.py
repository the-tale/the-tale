# coding: utf-8

from rels import Column
from rels.django import DjangoEnum

from questgen.relations import OPTION_MARKERS as QUEST_OPTION_MARKERS

from the_tale.game.balance import constants as c
from the_tale.game.balance.power import Power

from the_tale.game.artifacts.relations import ARTIFACT_TYPE


class RISK_LEVEL(DjangoEnum):
    health_percent_to_rest = Column()
    experience_modifier = Column()
    power_modifier = Column()
    reward_modifier = Column()
    description = Column()

    records = ( ('VERY_HIGH', 0, u'очень высокий', 0.70, 1.30,  2.0,  2.00, u'больше опыта и наград за задания, +200% к влиянию и денежным наградам за задания'),
                ('HIGH',      1, u'высокий',       0.85, 1.15,  1.0,  1.00, u'немного больше опыта и наград за задания, +100% к влиянию и денежным наградам за задания'),
                ('NORMAL',    2, u'обычный',       1.00, 1.00,  0.0,  0.00, u'никакого влияния на опыт, награды и влияние героя'),
                ('LOW',       3, u'низкий',        1.15, 0.85, -1.0, -1.00, u'немного меньше опыта и наград за задания, -100% к влиянию и денежным наградам за задания'),
                ('VERY_LOW',  4, u'очень низкий',  1.30, 0.70, -2.0, -2.00, u'меньше опыта и наград за задания, -200% к влиянию и денежным наградам за задания') )



class PREFERENCE_TYPE(DjangoEnum):
    level_required = Column()
    base_name = Column()
    prepair_method = Column(unique=False)
    nullable = Column(unique=False)

    records = ( ('MOB', 0, u'любимая добыча', 8, 'mob', '_prepair_mob', True),
                ('PLACE', 1, u'родной город', 4, 'place', '_prepair_place', True),
                ('FRIEND', 2, u'соратник', 12, 'friend', '_prepair_person', True),
                ('ENEMY', 3, u'противник', 20, 'enemy', '_prepair_person', True),
                ('ENERGY_REGENERATION_TYPE', 4, u'религиозность', 1, 'energy_regeneration_type', '_prepair_energy_regeneration', False),
                ('EQUIPMENT_SLOT', 5, u'экипировка', 36, 'equipment_slot', '_prepair_equipment_slot', True),
                ('RISK_LEVEL', 6, u'уровень риска', 32, 'risk_level', '_prepair_risk_level', False),
                ('FAVORITE_ITEM', 7, u'любимая вещь', 28, 'favorite_item', '_prepair_equipment_slot', True),
                ('ARCHETYPE', 8, u'архетип', 16, 'archetype', '_prepair_archetype', False),
                ('COMPANION_DEDICATION', 9, u'отношение со спутником', 2, 'companion_dedication', '_prepair_companion_dedication', False),
                ('COMPANION_EMPATHY', 10, u'эмпатия', 24, 'companion_empathy', '_prepair_companion_empathy', False) )


class COMPANION_DEDICATION(DjangoEnum):
    block_multiplier = Column(unique=False)
    heal_spending_priority = Column()
    description = Column()

    records = ( ('EGOISM', 0, u'эгоизм', 1.0 + c.COMPANIONS_BLOCK_MULTIPLIER_HERO_DEDICATION_DELTA,  0.75, u'спутник чаще защищает героя в бою'),
                ('NORMAL', 1, u'нейтралитет', 1.0, 1.0, u'спутник защищает героя с обычной частотой'),
                ('ALTRUISM', 2, u'альтруизм', 1.0 - c.COMPANIONS_BLOCK_MULTIPLIER_HERO_DEDICATION_DELTA, 1.25, u'спутник реже защищает героя в бою'),
                ('EVERY_MAN_FOR_HIMSELF', 3, u'каждый сам за себя', 1.0 - c.COMPANIONS_BLOCK_MULTIPLIER_HERO_DEDICATION_DELTA, 0.0,
                 u'спутник реже защищает героя в бою, герой ничего не делает для лечения спутника, помощь герою не лечит спутника') )


class COMPANION_EMPATHY(DjangoEnum):
    habit_multiplier = Column()
    description = Column()

    records = ( ('EGOCENTRIC', 0, u'эгоцентрик', 1.0 - c.COMPANIONS_HABITS_DELTA,  u'черты спутника оказывают меньшее влияние на черты героя'),
                ('ORDINAL', 1, u'обыкновенный', 1.0, u'черты спутника оказывает обычное влияние на черты героя'),
                ('EMPATH', 2, u'эмпат', 1.0 + c.COMPANIONS_HABITS_DELTA, u'черты спутника оказывает большее влияние на черты героя') )


class MONEY_SOURCE(DjangoEnum):

    records = ( ('EARNED_FROM_LOOT', 0, u'заработано продажей добычи'),
                ('EARNED_FROM_ARTIFACTS', 1, u'заработано продажей артефактов'),
                ('EARNED_FROM_QUESTS', 2, u'заработано выполнением квестов'),
                ('EARNED_FROM_HELP', 3, u'получено от хранителя'),
                ('EARNED_FROM_HABITS', 4, u'получено от черт'),
                ('EARNED_FROM_COMPANIONS', 5, u'получено от спутников'),

                ('SPEND_FOR_HEAL', 1000, u'потрачено на лечение'),
                ('SPEND_FOR_ARTIFACTS', 1001, u'потрачено на покупку артефактов'),
                ('SPEND_FOR_SHARPENING', 1002, u'потрачено на заточку артефактов'),
                ('SPEND_FOR_USELESS', 1003, u'потрачено без пользы'),
                ('SPEND_FOR_IMPACT', 1004, u'потрачено на изменение влияния'),
                ('SPEND_FOR_EXPERIENCE', 1005, u'потрачено на обучение'),
                ('SPEND_FOR_REPAIRING', 1006, u'потрачено на починку'),
                ('SPEND_FOR_TAX', 1007, u'потрачено на пошлину'),
                ('SPEND_FOR_COMPANIONS', 1008, u'потрачено на спутников') )



class ITEMS_OF_EXPENDITURE(DjangoEnum):
    ui_id = Column()
    priority = Column(unique=False, primary=False)
    price_fraction = Column(unique=False, primary=False) # цена в доле от стандартной цены
    money_source = Column()
    description = Column()

    records = ( ('INSTANT_HEAL',        0, u'лечение',           'heal',       20, 0.3, MONEY_SOURCE.SPEND_FOR_HEAL,
                 u'Собирает деньги, чтобы поправить здоровье, когда понадобится.'),
                ('BUYING_ARTIFACT',     1, u'покупка артефакта', 'artifact',   4,  3.0, MONEY_SOURCE.SPEND_FOR_ARTIFACTS,
                 u'Планирует приобретение новой экипировки.'),
                ('SHARPENING_ARTIFACT', 2, u'заточка артефакта', 'sharpening', 3,  2.0, MONEY_SOURCE.SPEND_FOR_SHARPENING,
                 u'Собирает на улучшение экипировки.'),
                ('USELESS',             3, u'на себя', 'useless',    7,  0.4, MONEY_SOURCE.SPEND_FOR_USELESS,
                 u'Копит золото для не очень полезных но безусловно необходимых трат.'),
                ('IMPACT',              4, u'изменение влияния', 'impact',     4,  1.0, MONEY_SOURCE.SPEND_FOR_IMPACT,
                 u'Планирует накопить деньжат, чтобы повлиять на «запомнившегося» горожанина.'),
                ('EXPERIENCE',          5, u'обучение',          'experience', 2,  4.0, MONEY_SOURCE.SPEND_FOR_EXPERIENCE,
                 u'Копит деньги в надежде немного повысить свою грамотность.'),
                ('REPAIRING_ARTIFACT',  6, u'починка артефакта', 'repairing', 15, 1.5, MONEY_SOURCE.SPEND_FOR_REPAIRING,
                 u'Копит на починку экипировки'),
                ('HEAL_COMPANION',  7, u'лечение спутника', 'heal_companion', 10, 0.3, MONEY_SOURCE.SPEND_FOR_COMPANIONS,
                 u'Копит на лечение спутника')
              )


    @classmethod
    def get_quest_upgrade_equipment_fraction(cls):
        return cls.BUYING_ARTIFACT.price_fraction * 0.75




class EQUIPMENT_SLOT(DjangoEnum):
    artifact_type = Column(related_name='equipment_slot')
    default = Column(unique=False, single_type=False)

    # records sorted in order in which they must be placed in UI
    records = ( ('HAND_PRIMARY', 0, u'основная рука', ARTIFACT_TYPE.MAIN_HAND, 'default_weapon'),
                ('HAND_SECONDARY', 1, u'вспомогательная рука', ARTIFACT_TYPE.OFF_HAND, None),
                ('HELMET', 2, u'шлем', ARTIFACT_TYPE.HELMET, None),
                ('AMULET', 9, u'амулет', ARTIFACT_TYPE.AMULET, None),
                ('SHOULDERS', 3, u'наплечники', ARTIFACT_TYPE.SHOULDERS, None),
                ('PLATE', 4, u'доспех', ARTIFACT_TYPE.PLATE, 'default_plate'),
                ('GLOVES', 5, u'перчатки', ARTIFACT_TYPE.GLOVES, 'default_gloves'),
                ('CLOAK', 6, u'плащ', ARTIFACT_TYPE.CLOAK, None),
                ('PANTS', 7, u'штаны', ARTIFACT_TYPE.PANTS, 'default_pants'),
                ('BOOTS', 8, u'сапоги', ARTIFACT_TYPE.BOOTS, 'default_boots'),
                ('RING', 10, u'кольцо', ARTIFACT_TYPE.RING, None) )

    @classmethod
    def default_uids(cls):
        return [record.default for record in cls.records if record.default is not None]


class MODIFIERS(DjangoEnum):
    default = Column(unique=False, single_type=False)

    records = ( ('INITIATIVE', 0, u'инициатива', lambda: 1.0),
                ('HEALTH', 1, u'здоровье', lambda: 1.0),
                ('DAMAGE', 2, u'урон', lambda: 1.0),
                ('SPEED', 3, u'скорость', lambda: 1.0),
                ('MIGHT_CRIT_CHANCE', 4, u'шанс критического срабатвания способности Хранителя', lambda: 0.0),
                ('EXPERIENCE', 5, u'опыт', lambda: 1.0),
                ('MAX_BAG_SIZE', 6, u'максимальный размер рюкзака', lambda: 0),
                ('POWER', 7, u'влияние героя', lambda: 0.0),
                ('QUEST_MONEY_REWARD', 8, u'денежная награда за выполнение задения', lambda: 0.0),
                ('BUY_PRICE', 9, u'цена покупки', lambda: 0.0),
                ('SELL_PRICE', 10, u'цена продажи', lambda: 0.0),
                ('ITEMS_OF_EXPENDITURE_PRIORITIES', 11, u'приортет трат', lambda: {record:record.priority for record in ITEMS_OF_EXPENDITURE.records}),
                ('GET_ARTIFACT_FOR_QUEST', 12, u'получить артефакты за задания', lambda: c.ARTIFACT_FOR_QUEST_PROBABILITY),
                # ('BUY_BETTER_ARTIFACT', 13, u'купить лучший артефакт', lambda: 0),
                ('KILL_BEFORE_BATTLE', 14, u'убить монстра перед боем', lambda: False),
                ('PICKED_UP_IN_ROAD', 15, u'ехать на попутных телегах', lambda: False),
                ('POWER_TO_FRIEND', 16, u'бонус к влиянию на друга', lambda: 0.0),
                ('POWER_TO_ENEMY', 17, u'бонус к влиянию на врага', lambda: 0.0),
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
                ('SAFE_INTEGRITY', 45, u'вероятность сохранить целостность артефакта после боя', lambda: 0),
                ('COHERENCE_EXPERIENCE', 46, u'опыт слаженности спутника', lambda: 0),
                ('HABITS_SOURCES', 47, u'источники изменения черт', lambda: set()),
                ('BATTLES_PER_TURN', 48, u'веротяность начала битвы', lambda: 0),
                ('COMPANION_DAMAGE', 49, u'урон по спутнику', lambda: 0),
                ('COMPANION_DAMAGE_PROBABILITY', 50, u'вероятность урона по спутнику', lambda: c.COMPANIONS_WOUND_ON_DEFEND_PROBABILITY_FROM_WOUNDS),
                ('COMPANION_STEAL_MONEY', 51, u'что спутник крадёт деньги при посещении города', lambda: False),
                ('COMPANION_STEAL_ITEM', 52, u'что спутник крадёт предмет при посещении города', lambda: False),
                ('COMPANION_SPARE_PARTS', 53, u'при смерти спутника, герой получает очень дорогие запчасти', lambda: False),
                ('COMPANION_SAY_WISDOM', 54, u'спутник периодически изрекает мудрые мысли, дающие герою опыт', lambda: False),
                ('COMPANION_EXP_PER_HEAL', 55, u'герой получает опыт за каждый уход за спутником', lambda: False),
                ('COMPANION_EAT_CORPSES', 56, u'спутник восстанавливает здоровье, поедая трупы враго', lambda: False),
                ('COMPANION_REGENERATE', 57, u'спутник восстанавливает здоровье, после ухода за ним героя', lambda: False),
                ('COMPANION_MONEY_FOR_FOOD', 58, u'множитель денег, которые тратятся на еду для спутника', lambda: 1.0),
                ('COMPANION_DRINK_ARTIFACT', 59, u'спутник пропивает артефакты', lambda: False),
                ('COMPANION_EXORCIST', 60, u'спутник является экзорцистом', lambda: False),
                ('COMPANION_BLOCK_PROBABILITY', 61, u'вероятность, что спутник заблокирует удар врага', lambda: 1.0),
                ('COMPANION_TELEPORTATOR', 62, u'вероятность телепортировать героя между городами', lambda: 0),
                ('COMPANION_FLYER', 63, u'вероятность телепортировать героя в движении', lambda: 0),
                ('COMPANION_LEAVE_IN_PLACE', 64, u'вероятность, что спутник покинет героя в городе', lambda: 0),
                ('COMPANION_ABILITIES_LEVELS', 65, u'уровень способностей спутника', lambda: {}),
                ('COMPANION_STEAL_MONEY_MULTIPLIER', 66, u'множитель денег, когда спутник крадёт деньги при посещении города', lambda: 1.0),
                ('COMPANION_STEAL_ITEM_MULTIPLIER', 67, u'вероятсноть артефакта, когда спутник крадёт предмет при посещении города', lambda: 1.0),
                ('COMPANION_EAT_CORPSES_PROBABILITY', 69, u'вероятность, что спутник восстанавливает здоровье, поедая трупы враго', lambda: c.COMPANIONS_EATEN_CORPSES_PER_BATTLE),
                ('COMPANION_SAY_WISDOM_PROBABILITY', 70, u'вероятсность, что спутник периодически изрекает мудрые мысли, дающие герою опыт', lambda: c.COMPANIONS_EXP_PER_MOVE_PROBABILITY),
                ('COMPANION_EXP_PER_HEAL_PROBABILITY', 71, u'вероятность, что герой получает опыт за каждый уход за спутником', lambda: 1.0),
                ('COMPANION_REGENERATE_PROBABILITY', 72, u'вероятсность, что спутник восстанавливает здоровье, после ухода за ним героя', lambda: c.COMPANIONS_REGEN_ON_HEAL_PER_HEAL),
                ('COMPANION_DRINK_ARTIFACT_PROBABILITY', 73, u'вероятсность, что спутник пропивает артефакты', lambda: 1.0),
                ('COMPANION_EXORCIST_PROBABILITY', 74, u'шанс, что спутник изгонит демона', lambda: 1.0),
                ('COMPANION_MAX_HEALTH', 75, u'множитель максимального здоровья спутника', lambda: 1.0),
                ('COMPANION_MAX_COHERENCE', 76, u'максимальный уровень слаженности', lambda: 0),

                ('COMPANION_LIVING_HEAL', 77, u'шанс подлечить живого спутника', lambda: 0),
                ('COMPANION_CONSTRUCT_HEAL', 78, u'шанс подлечить конструкта', lambda: 0),
                ('COMPANION_UNUSUAL_HEAL', 79, u'шанс подлечить особого спутника', lambda: 0),

                ('COMPANION_LIVING_COHERENCE_SPEED', 80, u'скорость развития живого спутника', lambda: 1.0),
                ('COMPANION_CONSTRUCT_COHERENCE_SPEED', 81, u'скорость развития конструкта', lambda: 1.0),
                ('COMPANION_UNUSUAL_COHERENCE_SPEED', 82, u'скорость развития особого спутника', lambda: 1.0),

                ('CHARACTER_QUEST_PRIORITY', 83, u'приоритет заданий связанных с героем', lambda: 1.0),
                )


class HABIT_CHANGE_SOURCE(DjangoEnum):
    quest_marker = Column(unique=False, single_type=False)
    quest_default = Column(unique=False, single_type=False)
    correlation_requirements = Column(unique=False, single_type=False)
    honor = Column(unique=False)
    peacefulness = Column(unique=False)

    records = ( ('QUEST_HONORABLE', 0, u'выбор чести в задании игроком', QUEST_OPTION_MARKERS.HONORABLE,            False, None, c.HABITS_QUEST_ACTIVE_DELTA, 0.0),
                ('QUEST_DISHONORABLE', 1, u'выбор бесчестия в задании игроком', QUEST_OPTION_MARKERS.DISHONORABLE,  False, None, -c.HABITS_QUEST_ACTIVE_DELTA, 0.0),
                ('QUEST_AGGRESSIVE', 2, u'выборе агрессивности в задании игроком', QUEST_OPTION_MARKERS.AGGRESSIVE, False, None, 0.0, -c.HABITS_QUEST_ACTIVE_DELTA),
                ('QUEST_UNAGGRESSIVE', 3, u'выбор миролюбия в задании игроком', QUEST_OPTION_MARKERS.UNAGGRESSIVE,  False, None, 0.0, c.HABITS_QUEST_ACTIVE_DELTA),

                ('QUEST_HONORABLE_DEFAULT', 4, u'выбор чести в задании героем', QUEST_OPTION_MARKERS.HONORABLE,            True, False, c.HABITS_QUEST_PASSIVE_DELTA, 0.0),
                ('QUEST_DISHONORABLE_DEFAULT', 5, u'выбор бесчестия в задании героем', QUEST_OPTION_MARKERS.DISHONORABLE,  True, False, -c.HABITS_QUEST_PASSIVE_DELTA, 0.0),
                ('QUEST_AGGRESSIVE_DEFAULT', 6, u'выборе агрессивности в задании героем', QUEST_OPTION_MARKERS.AGGRESSIVE, True, False, 0.0, -c.HABITS_QUEST_PASSIVE_DELTA),
                ('QUEST_UNAGGRESSIVE_DEFAULT', 7, u'выбор миролюбия в задании героем', QUEST_OPTION_MARKERS.UNAGGRESSIVE,  True, False, 0.0, c.HABITS_QUEST_PASSIVE_DELTA),

                ('HELP_AGGRESSIVE', 8, u'помощь в бою',     None, None, None, 0.0, -c.HABITS_HELP_ABILITY_DELTA),
                ('HELP_UNAGGRESSIVE', 9, u'помощь вне боя', None, None, None, 0.0, c.HABITS_HELP_ABILITY_DELTA),
                ('ARENA_SEND', 10, u'отправка на арену',    None, None, None, 0.0, -c.HABITS_ARENA_ABILITY_DELTA),
                ('ARENA_LEAVE', 11, u'покидание арены',     None, None, None, 0.0, c.HABITS_ARENA_ABILITY_DELTA),

                ('COMPANION_DISHONORABLE', 12, u'спутник склоняет к бесчестию',                          None, None, None,  -c.HABITS_HELP_ABILITY_DELTA, 0.0),
                ('COMPANION_HONOR_NEUTRAL_1', 13, u'спутник склоняет к нейтральной чести 1',             None, None, False, -c.HABITS_HELP_ABILITY_DELTA, 0.0),
                ('COMPANION_HONOR_NEUTRAL_2', 14, u'спутник склоняет к нейтральной чести 2',             None, None, False, c.HABITS_HELP_ABILITY_DELTA, 0.0),
                ('COMPANION_HONORABLE', 15, u'спутнки склоняет к чести',                                 None, None, None,  c.HABITS_HELP_ABILITY_DELTA, 0.0),
                ('COMPANION_AGGRESSIVE', 16, u'спутнки склоняет к агрессивности',                        None, None, None,  0.0, -c.HABITS_HELP_ABILITY_DELTA),
                ('COMPANION_PEACEFULL_NEUTRAL_1', 17, u'спутник склоняет к нейтральной агрессивности 1', None, None, False, 0.0, -c.HABITS_HELP_ABILITY_DELTA),
                ('COMPANION_PEACEFULL_NEUTRAL_2', 18, u'спутник склоняет к нейтральной агрессивности 2', None, None, False, 0.0, c.HABITS_HELP_ABILITY_DELTA),
                ('COMPANION_PEACEFULL', 19, u'спутник склоняет к миролюбию',                             None, None, None,  0.0, c.HABITS_HELP_ABILITY_DELTA),
              )


class ENERGY_REGENERATION(DjangoEnum):
    delay = Column(unique=False)
    period = Column(unique=False)
    amount = Column(unique=False)
    length = Column(unique=False)
    linguistics_slugs = Column()

    _PERIOD = c.ANGEL_ENERGY_REGENERATION_PERIOD
    _AMOUNT = c.ANGEL_ENERGY_REGENERATION_AMAUNT
    _LENGTH = c.ANGEL_ENERGY_REGENERATION_LENGTH

    records = ( ('PRAY', 0, u'молитва',               1, 1 * _PERIOD, 1 * _AMOUNT, 1 * _LENGTH, ('pray', )),
                ('SACRIFICE', 1, u'жертвоприношение', 2, 2 * _PERIOD, 2 * _AMOUNT, 2 * _LENGTH, ('sacrifice_fire', 'sacrifice_blood', 'sacrifice_knife')),
                ('INCENSE', 2, u'благовония',         4, 4 * _PERIOD, 4 * _AMOUNT, 4 * _LENGTH, ('incense', )),
                ('SYMBOLS', 3, u'символы',            3, 3 * _PERIOD, 3 * _AMOUNT, 3 * _LENGTH, ('symbols_stone', 'symbols_ground', 'symbols_tree')),
                ('MEDITATION', 4, u'медитация',       2, 2 * _PERIOD, 2 * _AMOUNT, 2 * _LENGTH, ('meditation', )) )
