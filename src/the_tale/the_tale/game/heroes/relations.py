
import smart_imports

smart_imports.all()


class RISK_LEVEL(rels_django.DjangoEnum):
    health_percent_to_rest = rels.Column()
    experience_modifier = rels.Column()
    reward_modifier = rels.Column()

    # коэфициэнты подобраны экспериментальным путём так,
    # чтобы для каждого уровня строились хоть немного, но разные пути
    # см. также cell_travel_cost()
    expected_battle_complexity = rels.Column()

    description = rels.Column()

    records = (('VERY_HIGH', 0, 'очень высокий', 0.70, 1.30, 2.00, 0.0, 'Больше опыта и наград за задания, +200% к денежным наградам за задания. При поиске пути герой полностью игнорирует безопасность региона.'),
               ('HIGH', 1, 'высокий', 0.85, 1.15, 1.00, 0.5, 'Немного больше опыта и наград за задания, +100% к денежным наградам за задания. При поиске пути герой ценит транспорт региона больше безопасности'),
               ('NORMAL', 2, 'обычный', 1.00, 1.00, 0.00, 1.0, 'Никакого влияния на опыт, награды и влияние героя. При поиске пути герой одинаково учитывает и транспорт и безопасность региона.'),
               ('LOW', 3, 'низкий', 1.15, 0.85, -1.00, 2.0, 'Немного меньше опыта и наград за задания, -100% к денежным наградам за задания. При поиске пути герой ценит безопасность региона больше транспорта.'),
               ('VERY_LOW', 4, 'очень низкий', 1.30, 0.70, -2.00, 4.0, 'Меньше опыта и наград за задания, -200% к денежным наградам за задания. При поиске пути герой оценивает безопасность региона значительно сильнее транспорта.'))


class PREFERENCE_TYPE(rels_django.DjangoEnum):
    base_name = rels.Column()
    prepair_method = rels.Column(unique=False)
    nullable = rels.Column(unique=False)

    records = (('MOB', 0, 'любимая добыча', 'mob', '_prepair_mob', True),
               ('PLACE', 1, 'родной город', 'place', '_prepair_place', True),
               ('FRIEND', 2, 'соратник', 'friend', '_prepair_person', True),
               ('ENEMY', 3, 'противник', 'enemy', '_prepair_person', True),
               ('ENERGY_REGENERATION_TYPE', 4, 'религиозность', 'energy_regeneration_type', '_prepair_energy_regeneration', False),
               ('EQUIPMENT_SLOT', 5, 'экипировка', 'equipment_slot', '_prepair_equipment_slot', True),
               ('RISK_LEVEL', 6, 'уровень риска', 'risk_level', '_prepair_risk_level', False),
               ('FAVORITE_ITEM', 7, 'любимая вещь', 'favorite_item', '_prepair_equipment_slot', True),
               ('ARCHETYPE', 8, 'архетип', 'archetype', '_prepair_archetype', False),
               ('COMPANION_DEDICATION', 9, 'отношения со спутником', 'companion_dedication', '_prepair_companion_dedication', False),
               ('COMPANION_EMPATHY', 10, 'эмпатия', 'companion_empathy', '_prepair_companion_empathy', False),
               ('QUESTS_REGION', 11, 'центр области заданий', 'quests_region', '_prepair_place', True),
               ('QUESTS_REGION_SIZE', 12, 'размер области заданий', 'quests_region_size', '_prepair_quests_region_size', False))


class COMPANION_DEDICATION(rels_django.DjangoEnum):
    block_multiplier = rels.Column(unique=False)
    heal_spending_priority = rels.Column()
    description = rels.Column()

    records = (('EGOISM', 0, 'эгоизм', 1.0 + c.COMPANIONS_BLOCK_MULTIPLIER_HERO_DEDICATION_DELTA, 0.75, 'спутник чаще защищает героя в бою'),
               ('NORMAL', 1, 'нейтралитет', 1.0, 1.0, 'спутник защищает героя с обычной частотой'),
               ('ALTRUISM', 2, 'альтруизм', 1.0 - c.COMPANIONS_BLOCK_MULTIPLIER_HERO_DEDICATION_DELTA, 1.25, 'спутник реже защищает героя в бою'),
               ('EVERY_MAN_FOR_HIMSELF', 3, 'каждый сам за себя', 1.0 - c.COMPANIONS_BLOCK_MULTIPLIER_HERO_DEDICATION_DELTA, 0.0,
                'спутник реже защищает героя в бою, герой ничего не делает для лечения спутника, помощь герою не лечит спутника'))


class COMPANION_EMPATHY(rels_django.DjangoEnum):
    habit_multiplier = rels.Column()
    description = rels.Column()

    records = (('EGOCENTRIC', 0, 'эгоцентрик', 1.0 - c.COMPANIONS_HABITS_DELTA, 'черты спутника оказывают меньшее влияние на черты героя'),
               ('ORDINAL', 1, 'обыкновенный', 1.0, 'черты спутника оказывают обычное влияние на черты героя'),
               ('EMPATH', 2, 'эмпат', 1.0 + c.COMPANIONS_HABITS_DELTA, 'черты спутника оказывают большее влияние на черты героя'))


class MONEY_SOURCE(rels_django.DjangoEnum):

    records = (('EARNED_FROM_LOOT', 0, 'заработано продажей добычи'),
               ('EARNED_FROM_ARTIFACTS', 1, 'заработано продажей артефактов'),
               ('EARNED_FROM_QUESTS', 2, 'заработано выполнением квестов'),
               ('EARNED_FROM_HELP', 3, 'получено от хранителя'),
               ('EARNED_FROM_HABITS', 4, 'получено от черт'),
               ('EARNED_FROM_COMPANIONS', 5, 'получено от спутников'),
               ('EARNED_FROM_MASTERS', 6, 'получено от мастеров'),

               ('SPEND_FOR_HEAL', 1000, 'потрачено на лечение'),
               ('SPEND_FOR_ARTIFACTS', 1001, 'потрачено на покупку артефактов'),
               ('SPEND_FOR_SHARPENING', 1002, 'потрачено на заточку артефактов'),
               ('SPEND_FOR_USELESS', 1003, 'потрачено без пользы'),
               ('SPEND_FOR_IMPACT', 1004, 'потрачено на изменение влияния'),
               ('SPEND_FOR_EXPERIENCE', 1005, 'потрачено на обучение'),
               ('SPEND_FOR_REPAIRING', 1006, 'потрачено на починку'),
               ('SPEND_FOR_TAX', 1007, 'потрачено на пошлину'),
               ('SPEND_FOR_COMPANIONS', 1008, 'потрачено на спутников'))


class ITEMS_OF_EXPENDITURE(rels_django.DjangoEnum):
    ui_id = rels.Column()
    priority = rels.Column(unique=False, primary=False)
    price_fraction = rels.Column(unique=False, primary=False)  # цена в доле от стандартной цены
    money_source = rels.Column()
    description = rels.Column()

    records = (('INSTANT_HEAL', 0, 'лечение', 'heal', 20, 0.3, MONEY_SOURCE.SPEND_FOR_HEAL,
                'Собирает деньги, чтобы поправить здоровье, если понадобится.'),
               ('BUYING_ARTIFACT', 1, 'покупка артефакта', 'artifact', 4, 3.0, MONEY_SOURCE.SPEND_FOR_ARTIFACTS,
                'Планирует приобретение новой экипировки.'),
               ('SHARPENING_ARTIFACT', 2, 'заточка артефакта', 'sharpening', 3, 2.0, MONEY_SOURCE.SPEND_FOR_SHARPENING,
                'Собирает на улучшение экипировки.'),
               ('USELESS', 3, 'на себя', 'useless', 7, 0.4, MONEY_SOURCE.SPEND_FOR_USELESS,
                'Копит золото для не очень полезных, но безусловно необходимых, трат.'),
               ('EXPERIENCE', 5, 'обучение', 'experience', 2, 4.0, MONEY_SOURCE.SPEND_FOR_EXPERIENCE,
                'Копит деньги в надежде немного повысить свою грамотность.'),
               ('REPAIRING_ARTIFACT', 6, 'починка артефакта', 'repairing', 15, 1.5, MONEY_SOURCE.SPEND_FOR_REPAIRING,
                'Копит на починку экипировки'),
               ('HEAL_COMPANION', 7, 'лечение спутника', 'heal_companion', 10, 0.3, MONEY_SOURCE.SPEND_FOR_COMPANIONS,
                'Копит на лечение спутника, если оно понадобится'))

    @classmethod
    def get_quest_upgrade_equipment_fraction(cls):
        return cls.BUYING_ARTIFACT.price_fraction * 0.75


class EQUIPMENT_SLOT(rels_django.DjangoEnum):
    artifact_type = rels.Column(related_name='equipment_slot')
    default = rels.Column(unique=False, single_type=False, no_index=False)

    # records sorted in order in which they must be placed in UI
    records = (('HAND_PRIMARY', 0, 'основная рука', artifacts_relations.ARTIFACT_TYPE.MAIN_HAND, 'default_weapon'),
               ('HAND_SECONDARY', 1, 'вспомогательная рука', artifacts_relations.ARTIFACT_TYPE.OFF_HAND, None),
               ('HELMET', 2, 'шлем', artifacts_relations.ARTIFACT_TYPE.HELMET, None),
               ('AMULET', 9, 'амулет', artifacts_relations.ARTIFACT_TYPE.AMULET, None),
               ('SHOULDERS', 3, 'наплечники', artifacts_relations.ARTIFACT_TYPE.SHOULDERS, None),
               ('PLATE', 4, 'доспех', artifacts_relations.ARTIFACT_TYPE.PLATE, 'default_plate'),
               ('GLOVES', 5, 'перчатки', artifacts_relations.ARTIFACT_TYPE.GLOVES, 'default_gloves'),
               ('CLOAK', 6, 'плащ', artifacts_relations.ARTIFACT_TYPE.CLOAK, None),
               ('PANTS', 7, 'штаны', artifacts_relations.ARTIFACT_TYPE.PANTS, 'default_pants'),
               ('BOOTS', 8, 'сапоги', artifacts_relations.ARTIFACT_TYPE.BOOTS, 'default_boots'),
               ('RING', 10, 'кольцо', artifacts_relations.ARTIFACT_TYPE.RING, None))

    @classmethod
    def default_uids(cls):
        return [record.default for record in cls.records if record.default is not None]


class MODIFIERS(rels_django.DjangoEnum):
    default = rels.Column(unique=False, single_type=False)

    records = (('INITIATIVE', 0, 'инициатива', lambda: 1.0),
               ('HEALTH', 1, 'здоровье', lambda: 1.0),
               ('DAMAGE', 2, 'урон', lambda: 1.0),
               ('SPEED', 3, 'скорость', lambda: 1.0),
               ('MIGHT_CRIT_CHANCE', 4, 'шанс критического срабатвания способности Хранителя', lambda: 0.0),
               ('EXPERIENCE', 5, 'опыт', lambda: 1.0),
               ('MAX_BAG_SIZE', 6, 'максимальный размер рюкзака', lambda: 0),
               ('POWER', 7, 'влияние героя', lambda: 0.0),
               ('QUEST_MONEY_REWARD', 8, 'денежная награда за выполнение задения', lambda: 0.0),
               ('BUY_PRICE', 9, 'цена покупки', lambda: 0.0),
               ('SELL_PRICE', 10, 'цена продажи', lambda: 0.0),
               ('ITEMS_OF_EXPENDITURE_PRIORITIES', 11, 'приортет трат', lambda: {record: record.priority for record in ITEMS_OF_EXPENDITURE.records}),
               ('GET_ARTIFACT_FOR_QUEST', 12, 'получить артефакты за задания', lambda: c.ARTIFACT_FOR_QUEST_PROBABILITY),
               ('KILL_BEFORE_BATTLE', 14, 'убить монстра перед боем', lambda: False),
               ('PICKED_UP_IN_ROAD', 15, 'ехать на попутных телегах', lambda: False),
               ('QUEST_MARKERS', 18, 'маркеры задания', lambda: {}),
               ('QUEST_MARKERS_REWARD_BONUS', 19, 'бонус наград за правильный выбор', lambda: {}),
               ('LOOT_PROBABILITY', 21, 'вероятность получить лут после боя', lambda: 1.0),
               ('EXP_FOR_KILL', 22, 'опыт за убийство моснтра', lambda: 1.0),
               ('PEACEFULL_BATTLE', 23, 'мирный бой', lambda: False),
               ('FRIEND_QUEST_PRIORITY', 24, 'приоритет задания на помощь другу', lambda: 1.0),
               ('ENEMY_QUEST_PRIORITY', 25, 'приоритет задания на вредительство врагу', lambda: 1.0),
               ('HONOR_EVENTS', 26, 'события для черт', lambda: set()),
               ('SAFE_ARTIFACT_INTEGRITY', 27, 'сохранить целостность артефакта', lambda: 0),
               ('MAGIC_DAMAGE', 28, 'бонус к магическому урону', lambda: 1.0),
               ('PHYSIC_DAMAGE', 29, 'бонус к физическому урону', lambda: 1.0),
               ('REST_LENGTH', 31, 'длительность отдыха', lambda: 1.0),
               ('RESURRECT_LENGTH', 32, 'длительность воскрешения', lambda: 1.0),
               ('IDLE_LENGTH', 33, 'длительность бездействия', lambda: 1.0),
               ('DOUBLE_ENERGY_REGENERATION', 35, 'вероятность восстановить в 2 раза больше энергии', lambda: 0),
               ('BONUS_ARTIFACT_POWER', 36, 'бонус к силе артефактов получаемых', lambda: power.Power(0, 0)),
               ('ADDITIONAL_ABILITIES', 37, 'дополнительные способности', lambda: []),
               ('FEAR', 39, 'монстры могу убежать в начале боя', lambda: 0),
               ('CLOUDED_MIND', 40, 'поступки героя перестают зависеть от черт', lambda: False),
               ('RARE', 41, 'увеличиена вероятность получить редкий артефакт', lambda: 1),
               ('EPIC', 42, 'увеличиена вероятность получить эпический артефакт', lambda: 1),
               ('HABITS_INCREASE', 43, 'скорость роста черт', lambda: 1),
               ('HABITS_DECREASE', 44, 'скорость уменьшения черт', lambda: 1),
               ('SAFE_INTEGRITY', 45, 'вероятность сохранить целостность артефакта после боя', lambda: 0),
               ('COHERENCE_EXPERIENCE', 46, 'опыт слаженности спутника', lambda: 1),
               ('HABITS_SOURCES', 47, 'источники изменения черт', lambda: set()),
               ('BATTLES_PER_TURN', 48, 'веротяность начала битвы', lambda: 0),
               ('COMPANION_DAMAGE', 49, 'урон по спутнику', lambda: 0),
               ('COMPANION_DAMAGE_PROBABILITY', 50, 'вероятность урона по спутнику', lambda: c.COMPANIONS_WOUND_ON_DEFEND_PROBABILITY_FROM_WOUNDS),
               ('COMPANION_STEAL_MONEY', 51, 'что спутник крадёт деньги при посещении города', lambda: False),
               ('COMPANION_STEAL_ITEM', 52, 'что спутник крадёт предмет при посещении города', lambda: False),
               ('COMPANION_SPARE_PARTS', 53, 'при смерти спутника, герой получает очень дорогие запчасти', lambda: False),
               ('COMPANION_SAY_WISDOM', 54, 'спутник периодически изрекает мудрые мысли, дающие герою опыт', lambda: False),
               ('COMPANION_EXP_PER_HEAL', 55, 'герой получает опыт за каждый уход за спутником', lambda: False),
               ('COMPANION_EAT_CORPSES', 56, 'спутник восстанавливает здоровье, поедая трупы враго', lambda: False),
               ('COMPANION_REGENERATE', 57, 'спутник восстанавливает здоровье, после ухода за ним героя', lambda: False),
               ('COMPANION_MONEY_FOR_FOOD', 58, 'множитель денег, которые тратятся на еду для спутника', lambda: 1.0),
               ('COMPANION_DRINK_ARTIFACT', 59, 'спутник пропивает артефакты', lambda: False),
               ('COMPANION_EXORCIST', 60, 'спутник является экзорцистом', lambda: False),
               ('COMPANION_BLOCK_PROBABILITY', 61, 'вероятность, что спутник заблокирует удар врага', lambda: 1.0),
               ('COMPANION_TELEPORTATOR', 62, 'вероятность телепортировать героя между городами', lambda: 0),
               ('COMPANION_FLYER', 63, 'вероятность телепортировать героя в движении', lambda: 0),
               ('COMPANION_LEAVE_IN_PLACE', 64, 'вероятность, что спутник покинет героя в городе', lambda: 0),
               ('COMPANION_ABILITIES_LEVELS', 65, 'уровень способностей спутника', lambda: {}),
               ('COMPANION_STEAL_MONEY_MULTIPLIER', 66, 'множитель денег, когда спутник крадёт деньги при посещении города', lambda: 1.0),
               ('COMPANION_STEAL_ITEM_MULTIPLIER', 67, 'вероятсноть артефакта, когда спутник крадёт предмет при посещении города', lambda: 1.0),
               ('COMPANION_EAT_CORPSES_PROBABILITY', 69, 'вероятность, что спутник восстанавливает здоровье, поедая трупы враго', lambda: c.COMPANIONS_EATEN_CORPSES_PER_BATTLE),
               ('COMPANION_SAY_WISDOM_PROBABILITY', 70, 'вероятсность, что спутник периодически изрекает мудрые мысли, дающие герою опыт', lambda: c.COMPANIONS_EXP_PER_MOVE_PROBABILITY),
               ('COMPANION_EXP_PER_HEAL_PROBABILITY', 71, 'вероятность, что герой получает опыт за каждый уход за спутником', lambda: 1.0),
               ('COMPANION_REGENERATE_PROBABILITY', 72, 'вероятсность, что спутник восстанавливает здоровье, после ухода за ним героя', lambda: c.COMPANIONS_REGEN_ON_HEAL_PER_HEAL),
               ('COMPANION_DRINK_ARTIFACT_PROBABILITY', 73, 'вероятсность, что спутник пропивает артефакты', lambda: 1.0),
               ('COMPANION_EXORCIST_PROBABILITY', 74, 'шанс, что спутник изгонит демона', lambda: 1.0),
               ('COMPANION_MAX_HEALTH', 75, 'множитель максимального здоровья спутника', lambda: 1.0),
               ('COMPANION_MAX_COHERENCE', 76, 'максимальный уровень слаженности', lambda: 0),

               ('COMPANION_LIVING_HEAL', 77, 'шанс подлечить живого спутника', lambda: 0),
               ('COMPANION_CONSTRUCT_HEAL', 78, 'шанс подлечить конструкта', lambda: 0),
               ('COMPANION_UNUSUAL_HEAL', 79, 'шанс подлечить особого спутника', lambda: 0),

               ('COMPANION_LIVING_COHERENCE_SPEED', 80, 'скорость развития живого спутника', lambda: 1.0),
               ('COMPANION_CONSTRUCT_COHERENCE_SPEED', 81, 'скорость развития конструкта', lambda: 1.0),
               ('COMPANION_UNUSUAL_COHERENCE_SPEED', 82, 'скорость развития особого спутника', lambda: 1.0),

               ('CHARACTER_QUEST_PRIORITY', 83, 'приоритет заданий связанных с героем', lambda: 1.0))


class HABIT_CHANGE_SOURCE(rels_django.DjangoEnum):
    quest_marker = rels.Column(unique=False, single_type=False)
    quest_default = rels.Column(unique=False, single_type=False)
    correlation_requirements = rels.Column(unique=False, single_type=False)
    honor = rels.Column(unique=False)
    peacefulness = rels.Column(unique=False)

    records = (('QUEST_HONORABLE', 0, 'выбор чести в задании игроком', questgen_relations.OPTION_MARKERS.HONORABLE, False, None, c.HABITS_QUEST_ACTIVE_DELTA, 0.0),
               ('QUEST_DISHONORABLE', 1, 'выбор бесчестия в задании игроком', questgen_relations.OPTION_MARKERS.DISHONORABLE, False, None, -c.HABITS_QUEST_ACTIVE_DELTA, 0.0),
               ('QUEST_AGGRESSIVE', 2, 'выборе агрессивности в задании игроком', questgen_relations.OPTION_MARKERS.AGGRESSIVE, False, None, 0.0, -c.HABITS_QUEST_ACTIVE_DELTA),
               ('QUEST_UNAGGRESSIVE', 3, 'выбор миролюбия в задании игроком', questgen_relations.OPTION_MARKERS.UNAGGRESSIVE, False, None, 0.0, c.HABITS_QUEST_ACTIVE_DELTA),

               ('QUEST_HONORABLE_DEFAULT', 4, 'выбор чести в задании героем', questgen_relations.OPTION_MARKERS.HONORABLE, True, False, c.HABITS_QUEST_PASSIVE_DELTA, 0.0),
               ('QUEST_DISHONORABLE_DEFAULT', 5, 'выбор бесчестия в задании героем', questgen_relations.OPTION_MARKERS.DISHONORABLE, True, False, -c.HABITS_QUEST_PASSIVE_DELTA, 0.0),
               ('QUEST_AGGRESSIVE_DEFAULT', 6, 'выборе агрессивности в задании героем', questgen_relations.OPTION_MARKERS.AGGRESSIVE, True, False, 0.0, -c.HABITS_QUEST_PASSIVE_DELTA),
               ('QUEST_UNAGGRESSIVE_DEFAULT', 7, 'выбор миролюбия в задании героем', questgen_relations.OPTION_MARKERS.UNAGGRESSIVE, True, False, 0.0, c.HABITS_QUEST_PASSIVE_DELTA),

               ('HELP_AGGRESSIVE', 8, 'помощь в бою', None, None, None, 0.0, -c.HABITS_HELP_ABILITY_DELTA),
               ('HELP_UNAGGRESSIVE', 9, 'помощь вне боя', None, None, None, 0.0, c.HABITS_HELP_ABILITY_DELTA),
               ('ARENA_SEND', 10, 'отправка на арену', None, None, None, 0.0, -c.HABITS_ARENA_ABILITY_DELTA),
               ('ARENA_LEAVE', 11, 'покидание арены', None, None, None, 0.0, c.HABITS_ARENA_ABILITY_DELTA),

               ('COMPANION_DISHONORABLE', 12, 'спутник склоняет к бесчестию', None, None, None, -c.HABITS_HELP_ABILITY_DELTA, 0.0),
               ('COMPANION_HONOR_NEUTRAL_1', 13, 'спутник склоняет к нейтральной чести 1', None, None, False, -c.HABITS_HELP_ABILITY_DELTA, 0.0),
               ('COMPANION_HONOR_NEUTRAL_2', 14, 'спутник склоняет к нейтральной чести 2', None, None, False, c.HABITS_HELP_ABILITY_DELTA, 0.0),
               ('COMPANION_HONORABLE', 15, 'спутнки склоняет к чести', None, None, None, c.HABITS_HELP_ABILITY_DELTA, 0.0),
               ('COMPANION_AGGRESSIVE', 16, 'спутнки склоняет к агрессивности', None, None, None, 0.0, -c.HABITS_HELP_ABILITY_DELTA),
               ('COMPANION_PEACEFULL_NEUTRAL_1', 17, 'спутник склоняет к нейтральной агрессивности 1', None, None, False, 0.0, -c.HABITS_HELP_ABILITY_DELTA),
               ('COMPANION_PEACEFULL_NEUTRAL_2', 18, 'спутник склоняет к нейтральной агрессивности 2', None, None, False, 0.0, c.HABITS_HELP_ABILITY_DELTA),
               ('COMPANION_PEACEFULL', 19, 'спутник склоняет к миролюбию', None, None, None, 0.0, c.HABITS_HELP_ABILITY_DELTA),

               ('MASTER_QUEST_HONORABLE', 20, 'бонус от мастера к чести', questgen_relations.OPTION_MARKERS.HONORABLE, None, None, c.HABITS_QUEST_PASSIVE_DELTA, 0.0),
               ('MASTER_QUEST_DISHONORABLE', 21, 'бонус от мастера к бесчестью', questgen_relations.OPTION_MARKERS.DISHONORABLE, None, None, -c.HABITS_QUEST_PASSIVE_DELTA, 0.0),
               ('MASTER_QUEST_AGGRESSIVE', 22, 'бонус от мастера к аггресивности', questgen_relations.OPTION_MARKERS.AGGRESSIVE, None, None, 0.0, -c.HABITS_QUEST_PASSIVE_DELTA),
               ('MASTER_QUEST_UNAGGRESSIVE', 23, 'бонус от мастера к миролюбию', questgen_relations.OPTION_MARKERS.UNAGGRESSIVE, None, None, 0.0, c.HABITS_QUEST_PASSIVE_DELTA))


class ENERGY_REGENERATION(rels_django.DjangoEnum):
    delay = rels.Column(unique=False)
    period = rels.Column(unique=False)
    amount = rels.Column(unique=False)
    length = rels.Column(unique=False)
    linguistics_slugs = rels.Column()

    _PERIOD = c.ANGEL_ENERGY_REGENERATION_PERIOD
    _AMOUNT = c.ANGEL_ENERGY_REGENERATION_AMAUNT
    _LENGTH = c.ANGEL_ENERGY_REGENERATION_LENGTH

    records = (('PRAY', 0, 'молитва', 1, 1 * _PERIOD, 1 * _AMOUNT, 1 * _LENGTH, ('pray', )),
               ('SACRIFICE', 1, 'жертвоприношение', 2, 2 * _PERIOD, 2 * _AMOUNT, 2 * _LENGTH, ('sacrifice_fire', 'sacrifice_blood', 'sacrifice_knife')),
               ('INCENSE', 2, 'благовония', 4, 4 * _PERIOD, 4 * _AMOUNT, 4 * _LENGTH, ('incense', )),
               ('SYMBOLS', 3, 'символы', 3, 3 * _PERIOD, 3 * _AMOUNT, 3 * _LENGTH, ('symbols_stone', 'symbols_ground', 'symbols_tree')),
               ('MEDITATION', 4, 'медитация', 2, 2 * _PERIOD, 2 * _AMOUNT, 2 * _LENGTH, ('meditation', )))


class CLAN_MEMBERSHIP(rels_django.DjangoEnum):
    records = (('NOT_IN_CLAN', 0, 'не состоит в гильдии'),
               ('IN_CLAN', 1, 'состоит в гильдии'))


class PROTECTORAT_OWNERSHIP(rels_django.DjangoEnum):
    records = (('HAS_PROTECTORAT', 0, 'гильдия героя — протектор города, в окрестнотсях которого тот находится'),
               ('NO_PROTECTORAT', 1, 'гильдия героя не является протектором города, в окрестнотсях которого тот находится'))
