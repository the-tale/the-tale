# coding: utf-8
import math

from the_tale.game.balance import helpers as h

TIME_TO_LVL_DELTA = float(7) # разница во времени получения двух соседних уровней
TIME_TO_LVL_MULTIPLIER = float(1.02) # множитель опыта, возводится в степень уровня

INITIAL_HP = int(500) # начальное здоровье героя

HP_PER_LVL = int(50) # бонус к здоровью на уровень

MOB_HP_MULTIPLIER = float(0.25) # какой процент здоровье среднего моба составляет от здоровья героя
BOSS_HP_MULTIPLIER = float(0.5) # какой процент здоровье среднего моба составляет от здоровья героя

TURN_DELTA = int(10)  # в секундах - задержка одного хода

TURNS_IN_HOUR = float(60.0 * 60 / TURN_DELTA) # количество ходов в 1 часе

POWER_PER_LVL = int(1) # значение "чистой" силы героя (т.е. без артефактов)

EQUIP_SLOTS_NUMBER = int(11) # количество слотов экипировки

# за скорость получения артефактов принимаем скорость получения их из лута
# остальные способы получения (покупка, квесты) считаем флуктуациями
ARTIFACTS_LOOT_PER_DAY = float(2.0) # количество новых артефактов, в реальный день
ARTIFACT_FOR_QUEST_PROBABILITY = float(0.2) # вероятность получить артефакт в награда за квест

# Доли лута и артефактов в доходах героя. В артефакты влючены и награды за задания.
INCOME_LOOT_FRACTION = float(0.6)
INCOME_ARTIFACTS_FRACTION = float(1.0 - INCOME_LOOT_FRACTION)

# магическое число — ожидаемое количество выполненных героем квестов в день
EXPECTED_QUESTS_IN_DAY = float(2.0)

# количество поломок артефактов в день, расчитывается так, чтобы за 3 недели в идеальном случае была обновлена вся экипировка
ARTIFACTS_BREAKING_SPEED = float(EQUIP_SLOTS_NUMBER / (3*7.0))

EQUIPMENT_BREAK_FRACTION = float(0.5) # доля артифактов в экипировке, которые могут сломаться
NORMAL_SLOT_REPAIR_PRIORITY = float(1.0)  # приоритет починки обычного слота
SPECIAL_SLOT_REPAIR_PRIORITY = float(2.0) # приоритет починки слота из предпочтения

EXP_PER_HOUR = int(10)  # опыт в час
EXP_PER_QUEST_FRACTION = float(0.33) # разброс опыта за задание

COMPANIONS_BONUS_EXP_FRACTION = float(0.2) # доля бонусного опыта, которую могут приносить спутники

# с учётом возможных способностей (т.е. считаем, что при нужных абилках у премиума скорость получения опыта будет 1.0)
EXP_FOR_PREMIUM_ACCOUNT = float(1.0) # модификатор опыта для премиум аккаунтов
EXP_FOR_NORMAL_ACCOUNT = float(0.66) # модификатор опыта для обычных акканутов

# TODO: привести EXP_FOR_PREMIUM_ACCOUNT к 1.0 (разница с нормальным аккаунтом должна быть 50%)
#       сейчас это сделать нельзя т.к. паливо


HERO_MOVE_SPEED = float(0.3) # базовая скорость героя расстояние в ход

BATTLE_LENGTH = int(16) # ходов - средняя длительность одного боя (количество действий в бой)
INTERVAL_BETWEEN_BATTLES = int(3) # ходов - время, между двумя битвами

BATTLES_BEFORE_HEAL = int(8) # количество боёв в непрерывной цепочке битв

MOVE_TURNS_IN_ACTION_CYCLE = INTERVAL_BETWEEN_BATTLES * BATTLES_BEFORE_HEAL

DISTANCE_IN_ACTION_CYCLE = HERO_MOVE_SPEED * MOVE_TURNS_IN_ACTION_CYCLE

HEAL_TIME_FRACTION = float(0.2) # доля времени от цепочки битв, которую занимает полный отхил героя
HEAL_STEP_FRACTION = float(0.2) # разброс регенерации за один ход

HEALTH_IN_SETTLEMENT_TO_START_HEAL_FRACTION = float(0.33) # если у героя здоровья меньше, чем указанная доля и он в городе, то он будет лечиться
HEALTH_IN_MOVE_TO_START_HEAL_FRACTION = float(2 * (1.0 / BATTLES_BEFORE_HEAL)) # если у героя здоровья меньше, чем указанная доля и он в походе, то он будет лечиться

TURNS_TO_IDLE = int(6) # количество ходов на уровень, которое герой бездельничает в соответствующей action
TURNS_TO_RESURRECT = int(TURNS_TO_IDLE * 3) # количество ходов на уровень, необходимое для воскрешения


GET_LOOT_PROBABILITY = float(0.50) # вероятность получить добычу после боя, если не получен артефакт

# вероятности получить разный тип добычи

EPIC_ARTIFACT_PROBABILITY = float(0.005)
RARE_ARTIFACT_PROBABILITY = float(0.05)
NORMAL_ARTIFACT_PROBABILITY = float(1 - RARE_ARTIFACT_PROBABILITY - EPIC_ARTIFACT_PROBABILITY)

NORMAL_LOOT_COST = float(1) #стоимость разной добычи на единицу уровня

MAX_BAG_SIZE = int(12) # максимальный размер рюкзака героя
BAG_SIZE_TO_SELL_LOOT_FRACTION = float(0.33) # процент заполненности рюкзака, после которого герой начнёт продавать вещи

# относительные размеры различных трат

BASE_EXPERIENCE_FOR_MONEY_SPEND = int(24 * EXP_PER_HOUR * 0.4)
EXPERIENCE_DELTA_FOR_MONEY_SPEND = float(0.5)

POWER_TO_LVL = float(EQUIP_SLOTS_NUMBER) # бонус к ожидаемой силе на уровнеь героя

# Разброс силы артефактов делаем от -ItemPowerDelta до +ItemPowerDelta.
# за базу берём количество слотов, т.е., теоретически, может не быть предметов с повторяющейся силой
# что бы не вводить дизбаланса, надо на маленьких уровнях уменьшать делту, что бу разница уровня предмета и дельты была неменьше единицы
ARTIFACT_POWER_DELTA = float(0.2) # дельта, на которую может изменяться сила артифакта

ARTIFACT_BETTER_MIN_POWER_DELTA = int(5) # минимальная дельта, на которую может изменятся сила лучшего артефакта (для магазина)

# ходов - длинна непрерывной цепочки боёв до остановки на лечение
BATTLES_LINE_LENGTH = int(BATTLES_BEFORE_HEAL * (BATTLE_LENGTH + INTERVAL_BETWEEN_BATTLES ) - INTERVAL_BETWEEN_BATTLES)

# количество битв в ход в промежутке непрерывных боёв
BATTLES_PER_TURN = float(1.0 / (INTERVAL_BETWEEN_BATTLES + 1) )
WHILD_BATTLES_PER_TURN_BONUS = float(0.05)

# максимально допустимое значение вероятности битв в час
MAX_BATTLES_PER_TURN = float(0.9)

COMPANIONS_DEFENDS_IN_BATTLE = float(1.5) # среднее количество «защит» героя средним спутником за 1 бой
COMPANIONS_HEAL_FRACTION = float(0.05) # доля действия уход за спутнкиком со средним количеством здоровья от всех действий героя

HEAL_LENGTH = int(math.floor(BATTLES_LINE_LENGTH * HEAL_TIME_FRACTION)) # ходов - длительность лечения героя

ACTIONS_CYCLE_LENGTH = int(math.ceil((BATTLES_LINE_LENGTH + HEAL_LENGTH) / (1 - COMPANIONS_HEAL_FRACTION))) # ходов - длинна одного "игрового цикла" - цепочка боёв + хил

MOVE_TURNS_IN_HOUR = MOVE_TURNS_IN_ACTION_CYCLE * (ACTIONS_CYCLE_LENGTH * TURN_DELTA / float(60*60))

# примерное количество боёв, которое будет происходить в час игрового времени
BATTLES_PER_HOUR = TURNS_IN_HOUR * (float(BATTLES_BEFORE_HEAL) / ACTIONS_CYCLE_LENGTH)

# вероятность выпаденя артефакта из моба (т.е. вероятноть получить артефакт после боя)
ARTIFACTS_PER_BATTLE = float(ARTIFACTS_LOOT_PER_DAY / (BATTLES_PER_HOUR * 24))

# вероятность сломать артефакт после боя
ARTIFACTS_BREAKS_PER_BATTLE = float(ARTIFACTS_BREAKING_SPEED / (BATTLES_PER_HOUR * 24))

ARTIFACT_FROM_PREFERED_SLOT_PROBABILITY = float(0.25) # вероятность выбрать для покупки/обновления артефакт из предпочитаемого слота

ARTIFACT_INTEGRITY_DAMAGE_PER_BATTLE = int(1) # уменьшение целостности артефактов за бой
ARTIFACT_INTEGRITY_DAMAGE_FOR_FAVORITE_ITEM = float(0.5) # модификатор повреждений целостности любимого предмета

_INTEGRITY_LOST_IN_DAY = BATTLES_PER_HOUR * 24 * ARTIFACT_INTEGRITY_DAMAGE_PER_BATTLE

ARTIFACT_RARE_MAX_INTEGRITY_MULTIPLIER = float(1.5) # коофициент увеличения максимальной целостности для редких артефактов
ARTIFACT_EPIC_MAX_INTEGRITY_MULTIPLIER = float(2) # коофициент увеличения максимальной целостности для эпических артефактов
ARTIFACT_MAX_INTEGRITY_DELTA = float(0.25) # разброс допустимой максимальной целостности

ARTIFACT_MAX_INTEGRITY = int(round(_INTEGRITY_LOST_IN_DAY * 30, -3)) # максимальная целостность обычного артефакта
ARTIFACT_SHARP_MAX_INTEGRITY_LOST_FRACTION = float(0.02) # доля максимальной целостности, теряемая при заточке
ARTIFACT_INTEGRITY_SAFE_BARRIER = float(0.2) # доля от максимальной целостности, артефакт не может сломаться, если его целостность отличается от максимальной меньше чем на эту долю
ARTIFACT_BREAK_POWER_FRACTIONS = (float(0.2), float(0.3)) # на сколько артефакт может сломаться за раз
ARTIFACT_BREAK_INTEGRITY_FRACTIONS = (float(0.1), float(0.2)) # на сколько артефакт может сломаться за раз

PREFERENCES_CHANGE_DELAY = int(2*7*24*60*60) # время блокировки возможности изменять предпочтение

PREFERED_MOB_LOOT_PROBABILITY_MULTIPLIER = float(2) # множитель вероятности получения лута из любимой добычи

DAMAGE_TO_HERO_PER_HIT_FRACTION = float(1.0 / (BATTLES_BEFORE_HEAL * (BATTLE_LENGTH / 2 - COMPANIONS_DEFENDS_IN_BATTLE))) # доля урона, наносимого герою за удар
DAMAGE_TO_MOB_PER_HIT_FRACTION = float(1.0 / (BATTLE_LENGTH / 2)) # доля урона, наносимого мобу за удар
DAMAGE_DELTA = float(0.2) # разброс в значениях урона [1-DAMAGE_DELTA, 1+DAMAGE_DELTA]

DAMAGE_CRIT_MULTIPLIER = float(2.0) # во сколько раз увеличивается урон при критическом ударе

# таким образом, напрашиваются следующие параметры мобов:
# - здоровье, в долях от среднемобского - чем больше его, тем  дольше моб живёт
#  - инициатива, в долях относительно геройской - чем больше, тем чаще моб ходит
#  - урон, в долях от среднемобского - чем больше, тем больнее бьёт
#  - разброс урона, в долях от среднего - декоративный параметр, т.к. в итоге будет средний урон наноситься
# так как все параметры измеряются в долях, то сложность моба можно высчитать как hp * initiative * damage = 1 для среднего моба
# моб со всеми парамтрами, увеличеными на 10% будет иметь сложность 1.1^3 ~ 1.33
# соответственно, вводня для каждого параметра шаг в 0.1 и скалируя от 0.5 до 1.5, получим 11^3 вариантов параметров (и, соответственно поведения)
# сложность мобов в этом случае будет изменяться от 0.5^3 до 1.5^3 ~ (0.125, 3.375)
#
# возникает проблема обеспечения равномерности прокачки героев на разных территориях - для полностью честных условий необходимо обеспечить одинаковую сложность мобов,
# альтернативный вариант - изменять количесво опыта, даваемого за моба, в зависимости от его сложности, этот вариант кажется как более логичным с точки зрения игрока, так и простым в реализации, на нём и остановимся
#
# расчёт прочей добычи и золота: добыча/трата

# считаем, что если герой не выбил артефакт, то у него есть вероятность выбить добычу
# добычу делим на обычную, редкую и очень редкую
# добыча является основным источником дохода, вырученное за его продажу золото является функцией от уровня и редкости - т.е. есть три фунции от уровня
# добыча, как и мобы, организован в список, отсортированый по уровню, на котором он становится доступным, это позволит открывать игрокам новый контент, а так же сделать разброс цен



##########################
# разные левые "неприкаянные" константы
##########################

DESTINY_POINT_IN_LEVELS = int(5) # раз в сколько уровней давать очко абилок
SPEND_MONEY_FOR_HEAL_HEALTH_FRACTION = float(0.75) # герой будет тратить деньги на лечение, когда его здоровье будет меньше этого параметра

##########################
# параметры ангелов
##########################

ANGEL_ENERGY_REGENERATION_TIME = float(0.5) # раз в сколько часов регенерируем
ANGEL_ENERGY_REGENERATION_AMAUNT = int(1) # сколько восстанавливаем
ANGEL_ENERGY_REGENERATION_PERIOD = int(ANGEL_ENERGY_REGENERATION_TIME * TURNS_IN_HOUR) # раз в сколько ходов
ANGEL_ENERGY_IN_DAY = int(24.0 / ANGEL_ENERGY_REGENERATION_TIME * ANGEL_ENERGY_REGENERATION_AMAUNT)

ANGEL_ENERGY_REGENERATION_LENGTH = int(3) # сколько ходов будет идти ренерация единицы энергии

# энергия должна полностью регенериться за сутки, раз в 2 часа должна появляться новая мажка
ANGEL_ENERGY_FREE_MAX = int(ANGEL_ENERGY_IN_DAY / 3) # максимум энергии у неподписчиков
ANGEL_ENERGY_PREMIUM_MAX = int(ANGEL_ENERGY_IN_DAY * 1.5) # максимум энергии у подписчиков
ANGEL_FREE_ENERGY_MAXIMUM = int(ANGEL_ENERGY_IN_DAY * 2) # максимальное количество энергии, которые игрок может получить, используя помощь
ANGEL_FREE_ENERGY_CHARGE = int(10) # количество бонусной энергии при срабатывании помощи
ANGEL_FREE_ENERGY_CHARGE_CRIT = int(ANGEL_FREE_ENERGY_CHARGE * 2) # количество бонусной энергии при критическом срабатывании помощи



##########################
# абилки ангела
##########################

ANGEL_HELP_COST = int(4)
ANGEL_ARENA_COST = int(1)
ANGEL_ARENA_QUIT_COST = int(0)
ANGEL_DROP_ITEM_COST = int(3)

ANGEL_HELP_HEAL_IF_LOWER_THEN = float(0.8) # можем лечить если здоровья меньше чем

ANGEL_HELP_HEAL_FRACTION = (float(0.25), float(0.5)) # (min, max) процент хелсов, которые будут вылечины
ANGEL_HELP_TELEPORT_DISTANCE = float(3.0) # расстяние на которое происходит телепорт
ANGEL_HELP_LIGHTING_FRACTION = (float(0.25), float(0.5)) # (min, max) процент урона, который будет нанесён

# считаем, что при эпической удачливости все использования будут давать опыт
# и предполагаем, что можем разрешить (при такой удачливости), в день получать опыт как за такой же день
ANGEL_HELP_EXPERIENCE = int(24.0 * EXP_PER_HOUR / (ANGEL_ENERGY_IN_DAY / ANGEL_HELP_COST))

ANGEL_HELP_EXPERIENCE_DELTA = float(0.5)

ANGEL_HELP_CRIT_HEAL_FRACTION = (float(0.5), float(0.75)) # (min, max) процент хелсов, которые будут вылечины
ANGEL_HELP_CRIT_TELEPORT_DISTANCE = float(9.0) # расстяние на которое происходит телепорт
ANGEL_HELP_CRIT_LIGHTING_FRACTION = (float(0.5), float(0.75)) # (min, max) процент урона, который будет нанесён
ANGEL_HELP_CRIT_MONEY_MULTIPLIER = int(10)
ANGEL_HELP_CRIT_MONEY_FRACTION = (float(0.75), float(1.25))
ANGEL_HELP_CRIT_EXPERIENCE = int(ANGEL_HELP_EXPERIENCE * 3)


ANGEL_ENERGY_INSTANT_REGENERATION_IN_PLACE = ANGEL_HELP_COST

##########################
# игровое время из расчёта 1/4 дня в полчаса (считаем среднюю сессию в 15 минут, берём х2 запас), т.е. 1 игровой день == 2 часа реального времени
##########################

GAME_SECONDS_IN_GAME_MINUTE = int(60)
GAME_MINUTES_IN_GAME_HOUR = int(60)
GAME_HOURSE_IN_GAME_DAY = int(24)
GAME_DAYS_IN_GAME_WEEK = int(7)
GAME_WEEKS_IN_GAME_MONTH = int(4)
GAME_MONTH_IN_GAME_YEAR = int(4)

GAME_SECONDS_IN_GAME_HOUR = int(GAME_SECONDS_IN_GAME_MINUTE * GAME_MINUTES_IN_GAME_HOUR)
GAME_SECONDS_IN_GAME_DAY = int(GAME_SECONDS_IN_GAME_HOUR * GAME_HOURSE_IN_GAME_DAY)
GAME_SECONDS_IN_GAME_WEEK = int(GAME_SECONDS_IN_GAME_DAY * GAME_DAYS_IN_GAME_WEEK)
GAME_SECONDS_IN_GAME_MONTH = int(GAME_SECONDS_IN_GAME_WEEK * GAME_WEEKS_IN_GAME_MONTH)
GAME_SECONDS_IN_GAME_YEAR = int(GAME_SECONDS_IN_GAME_MONTH * GAME_MONTH_IN_GAME_YEAR)

_TURNS_IN_GAME_DAY = int(4 *(TURNS_IN_HOUR / 2))

TURNS_IN_GAME_MONTH = _TURNS_IN_GAME_DAY * GAME_DAYS_IN_GAME_WEEK * GAME_WEEKS_IN_GAME_MONTH
TURNS_IN_GAME_YEAR = TURNS_IN_GAME_MONTH * GAME_MONTH_IN_GAME_YEAR
GAME_SECONDS_IN_TURN = int(GAME_SECONDS_IN_GAME_DAY / _TURNS_IN_GAME_DAY)

##########################
# Карта
##########################

MAP_CELL_LENGTH = float(3.0) # длина клетки в километрах

QUEST_AREA_RADIUS = float(60 * MAP_CELL_LENGTH) # радиус от позиции героя в котором ОБЫЧНО выбираются города для его заданий
QUEST_AREA_SHORT_RADIUS = QUEST_AREA_RADIUS / 2 # радиус от позиции героя в котором выбираются города для его заданий на начальных уровнях
QUEST_AREA_MAXIMUM_RADIUS = float(1000000 * MAP_CELL_LENGTH) # максимальный радиус для выбора городов для заданий

# примерное количество ходов на один квест вида «сходит туда и обратно»
# средний квест предполагает среднее расстояние между городами, значит двойное расстоения надо поделить на 2
TURNS_IN_QUEST = QUEST_AREA_RADIUS * 2 / 2 / DISTANCE_IN_ACTION_CYCLE * ACTIONS_CYCLE_LENGTH

MAP_SYNC_TIME_HOURS = int(1)
MAP_SYNC_TIME = int(TURNS_IN_HOUR * MAP_SYNC_TIME_HOURS) # синхронизируем карту раз в N часов

##########################
# Задания
##########################

QUESTS_SHORT_PATH_LEVEL_CAP = int(4) # на уровнях до этого герои получаю задания в близких городах

QUESTS_PILGRIMAGE_FRACTION = float(0.025) # вероятность отправить героя в паломничество

##########################
# Влияние
##########################

HERO_POWER_PER_DAY = int(100) # базовое количество влияния, которое герой 1-ого уровня производит в день на одного жителя задействованного в заданиях
PERSON_POWER_PER_QUEST_FRACTION = float(0.33) # разброс влияния за задание
PERSON_POWER_FOR_RANDOM_SPEND = int(200)

MINIMUM_CARD_POWER = int(HERO_POWER_PER_DAY / 5)

NORMAL_JOB_LENGTH = int(10) # средняя длительность занятия мастера в днях

JOB_MIN_POWER = float(0.5)
JOB_MAX_POWER = float(2.0)

JOB_HERO_REWARD_FRACTION = float(0.1) # множитель наград для героев, расчитываемых из длительности проекта

##########################
# споособности
##########################

ABILITIES_ACTIVE_MAXIMUM = int(5)
ABILITIES_PASSIVE_MAXIMUM = int(2)

ABILITIES_BATTLE_MAXIMUM = ABILITIES_ACTIVE_MAXIMUM + ABILITIES_PASSIVE_MAXIMUM
ABILITIES_NONBATTLE_MAXIMUM = int(4)
ABILITIES_COMPANION_MAXIMUM = int(4)

ABILITIES_OLD_ABILITIES_FOR_CHOOSE_MAXIMUM = int(2)
ABILITIES_FOR_CHOOSE_MAXIMUM = int(4)

##########################
# Черты
##########################

HABITS_BORDER = int(1000) # модуль максимального значения черты
HABITS_RIGHT_BORDERS = [-700, -300, -100, 100, 300, 700, 1001] # правые границы черт
HABITS_QUEST_ACTIVE_DELTA = float(20) # за выбор в задании игроком
HABITS_QUEST_PASSIVE_DELTA = float(0.05 * HABITS_QUEST_ACTIVE_DELTA) # за неверный выбор героем
HABITS_HELP_ABILITY_DELTA = float(float(HABITS_BORDER) / (60 * ANGEL_ENERGY_IN_DAY / ANGEL_HELP_COST)) # за использование способности
HABITS_ARENA_ABILITY_DELTA = float(float(HABITS_BORDER) / (60 * ANGEL_ENERGY_IN_DAY / ANGEL_ARENA_COST)) # за использование способности

HABITS_QUEST_ACTIVE_PREMIUM_MULTIPLIER = float(1.5) # бонус к начисляемому влиянию за выбор игрока для подписчиков


KILL_BEFORE_BATTLE_PROBABILITY = float(0.05)  # вероятность убить мобы в начале боя
PICKED_UP_IN_ROAD_TELEPORT_LENGTH = ANGEL_HELP_TELEPORT_DISTANCE
# бонус к скорости передвижения, эквивалентный вероятности убить моба
PICKED_UP_IN_ROAD_SPEED_BONUS = h.speed_from_safety(BATTLES_PER_TURN*KILL_BEFORE_BATTLE_PROBABILITY, BATTLES_PER_TURN)
PICKED_UP_IN_ROAD_PROBABILITY = PICKED_UP_IN_ROAD_SPEED_BONUS / PICKED_UP_IN_ROAD_TELEPORT_LENGTH

HABIT_QUEST_PRIORITY_MODIFIER = float(1) # модификатор приоритета выбора заданий от предпочтений

HONOR_POWER_BONUS_FRACTION = float(1.5) # бонус к влиянию для чести
MONSTER_TYPE_BATTLE_CRIT_MAX_CHANCE = float(0.02) # вероятность крита по типу монстра, если все монстры этого типа

HABIT_QUEST_REWARD_MAX_BONUS = float(1.0) # максимальный бонус к награде за задание при выборе, совпадающем с чертой
HABIT_LOOT_PROBABILITY_MODIFIER = float(1.2) # бонус к вероятности получить любой лут

PEACEFULL_BATTLE_PROBABILITY = float(0.01) # вероятность мирно разойтись с монстром, если все можно расходиться со всеми типами монстров

# вероятность получить опыт расчитывается исходя из:
# - средней величины получаемого опыта
# - ускорения прокачки от первого удара (вычитается)
# - проигрыша агрессивного использования способностей (молния) перед мирными (телепортом) (плюсуется)
# - лечение не учитываем, т.к. оно может быть применено и в бою и не в бою

# процент сохранённых ходов от первого удара
_FIRST_STRIKE_TURNS_BONUS = (0.5 * BATTLES_BEFORE_HEAL) / ACTIONS_CYCLE_LENGTH # выигрываем полхода в каждой битве

_HELPS_IN_TURN = (float(ANGEL_ENERGY_IN_DAY) / ANGEL_HELP_COST) / 24 / TURNS_IN_HOUR

# процент сохранённых ходов сражения, если только бьём молнией
_BATTLE_TURNS_BONUS_FROM_ON_USE = (float(BATTLE_LENGTH) * (sum(ANGEL_HELP_LIGHTING_FRACTION)/2) + HEAL_LENGTH * (sum(ANGEL_HELP_HEAL_FRACTION)/2)) / 2
_BATTLE_TURNS_BONUS = _BATTLE_TURNS_BONUS_FROM_ON_USE * _HELPS_IN_TURN

# процент сохранённых ходов движения, если только телепортируем
_TELEPORT_MOVE_TURNS = float(ANGEL_HELP_TELEPORT_DISTANCE) / HERO_MOVE_SPEED
_TELEPORT_SAVED_BATTLES = _TELEPORT_MOVE_TURNS/INTERVAL_BETWEEN_BATTLES
_TELEPORT_SAVED_TURNS =_TELEPORT_MOVE_TURNS + _TELEPORT_SAVED_BATTLES * BATTLE_LENGTH + HEAL_LENGTH * _TELEPORT_SAVED_BATTLES / BATTLES_BEFORE_HEAL
_TELEPORT_TURNS_BONUS = _TELEPORT_SAVED_TURNS * _HELPS_IN_TURN

# процент сохранённых ходов от мирного расхождения с монстрами
_PEACEFULL_TURNS_BONUS = (PEACEFULL_BATTLE_PROBABILITY * float(BATTLES_BEFORE_HEAL) * BATTLE_LENGTH) / ACTIONS_CYCLE_LENGTH

# print 'battles in day', TURNS_IN_HOUR * 24 / ACTIONS_CYCLE_LENGTH * BATTLES_BEFORE_HEAL
# print 'inverted', 1.0 / (TURNS_IN_HOUR * 24 / ACTIONS_CYCLE_LENGTH * BATTLES_BEFORE_HEAL)
# print 'strike', _FIRST_STRIKE_TURNS_BONUS
# print 'battle', _BATTLE_TURNS_BONUS
# print 'teleport', _TELEPORT_TURNS_BONUS

EXP_FOR_KILL = int(2 * EXP_PER_HOUR) # средний опыт за убийство монстра
EXP_FOR_KILL_DELTA = float(0.3) # разброс опыта за убийство


_KILLS_IN_HOUR = float(TURNS_IN_HOUR) / ACTIONS_CYCLE_LENGTH * BATTLES_BEFORE_HEAL
_REQUIRED_EXP_BONUS = _TELEPORT_TURNS_BONUS + _PEACEFULL_TURNS_BONUS - _BATTLE_TURNS_BONUS - _FIRST_STRIKE_TURNS_BONUS

# вероятность получить опыт за убийство моба
EXP_FOR_KILL_PROBABILITY =  float(EXP_PER_HOUR * _REQUIRED_EXP_BONUS) / _KILLS_IN_HOUR / EXP_FOR_KILL

###########################
# события для черт
###########################

HABIT_EVENTS_IN_DAY = float(1.33) # количество событий в сутки
HABIT_EVENTS_IN_TURN = float(HABIT_EVENTS_IN_DAY / 24 / TURNS_IN_HOUR) # вероятность события в ход

HABIT_MOVE_EVENTS_IN_TURN = HABIT_EVENTS_IN_TURN / (BATTLES_BEFORE_HEAL * INTERVAL_BETWEEN_BATTLES / float(ACTIONS_CYCLE_LENGTH)) # вероятность события при движении
HABIT_IN_PLACE_EVENTS_IN_TURN = HABIT_MOVE_EVENTS_IN_TURN * 10 # вероятность события в городе (с учётом имплементации)

# приоритеты событий с разными эффектами
HABIT_EVENT_NOTHING_PRIORITY = float(4)
HABIT_EVENT_MONEY_PRIORITY = float(4)
HABIT_EVENT_ARTIFACT_PRIORITY = float(2)
HABIT_EVENT_EXPERIENCE_PRIORITY = float(1)

# получаемые деньги могут быть эквиваленты цене продажи артефакта
# артефакт может создаваться обычным (как при луте)
# считаем, что можем позволить ускорить прокачку на 5%
_HABIT_EVENT_TOTAL_PRIORITY = HABIT_EVENT_NOTHING_PRIORITY + HABIT_EVENT_MONEY_PRIORITY + HABIT_EVENT_ARTIFACT_PRIORITY + HABIT_EVENT_EXPERIENCE_PRIORITY
HABIT_EVENT_EXPERIENCE = int(0.05 * (24.0 * EXP_PER_HOUR) / (HABIT_EVENTS_IN_DAY * HABIT_EVENT_EXPERIENCE_PRIORITY / _HABIT_EVENT_TOTAL_PRIORITY) )
HABIT_EVENT_EXPERIENCE_DELTA = float(0.5) # разброс опыта

###########################
# pvp
###########################

DAMAGE_PVP_ADVANTAGE_MODIFIER = float(0.5) # на какую долю изменяется урон при максимальной разнице в преимуществе между бойцами
DAMAGE_PVP_FULL_ADVANTAGE_STRIKE_MODIFIER = float(5) # во сколько раз увеличится урон удара при максимальном преимушестве

PVP_MAX_ADVANTAGE_STEP = float(0.25)

PVP_ADVANTAGE_BARIER = float(0.95)
PVP_EFFECTIVENESS_EXTINCTION_FRACTION = float(0.1)

PVP_EFFECTIVENESS_STEP = float(10)
PVP_EFFECTIVENESS_INITIAL = float(300)

###########################
# города
###########################

PLACE_MIN_PERSONS = 2
PLACE_MAX_PERSONS = 6

PLACE_MIN_SAFETY = 0.05
PLACE_MIN_TRANSPORT = 0.1
PLACE_MIN_STABILITY = 0
PLACE_MIN_CULTURE = 0.2

PLACE_MAX_SIZE = int(10)
PLACE_MAX_ECONOMIC = int(10)
PLACE_MAX_FRONTIER_ECONOMIC = int(5)

PLACE_NEW_PLACE_LIVETIME = int(2*7*24*60*60)

PLACE_POWER_HISTORY_WEEKS = int(6) # количество недель, которое хранится влияние города
PLACE_POWER_HISTORY_LENGTH = int(PLACE_POWER_HISTORY_WEEKS*7*24*TURNS_IN_HOUR) # в ходах

PLACE_POWER_RECALCULATE_STEPS = float(PLACE_POWER_HISTORY_LENGTH) / MAP_SYNC_TIME
PLACE_POWER_REDUCE_FRACTION = float(math.pow(0.01, 1.0 / PLACE_POWER_RECALCULATE_STEPS))

PLACE_TYPE_NECESSARY_BORDER = int(75)
PLACE_TYPE_ENOUGH_BORDER = int(50)

PLACE_GOODS_BONUS = int(100) # в час, соответственно PLACE_GOODS_BONUS * LEVEL — прирост/убыль товаров в городе
PLACE_GOODS_TO_LEVEL = int(PLACE_GOODS_BONUS * (1 + 3.0/2) * 24) # 1 город + 3 средних жителя за 24 часа
PLACE_GOODS_AFTER_LEVEL_UP = float(0.25) # процент товаров, остающихся при увеличении размера города
PLACE_GOODS_AFTER_LEVEL_DOWN = float(0.75) # процент товаров, возвращающихся при уменьшении размера города

PLACE_KEEPERS_GOODS_SPENDING = float(0.05) # доля трат даров хранителей за один час

PLACE_GOODS_FROM_BEST_PERSON = int(PLACE_GOODS_BONUS / 2)

# исходим из того, что в первую очередь надо балансировать вероятность нападения монстров как самый важный параметр
PLACE_SAFETY_FROM_BEST_PERSON = float(0.025)
PLACE_TRANSPORT_FROM_BEST_PERSON = h.speed_from_safety(PLACE_SAFETY_FROM_BEST_PERSON, BATTLES_PER_TURN)

# хотя на опыт свобода и не влияет, но на город оказывает такое-же влияние как и транспорт
PLACE_FREEDOM_FROM_BEST_PERSON = PLACE_TRANSPORT_FROM_BEST_PERSON

PLACE_CULTURE_FROM_BEST_PERSON = float(0.15)

PLACE_RACE_CHANGE_DELTA_IN_DAY = float(0.1)
PLACE_RACE_CHANGE_DELTA = (PLACE_RACE_CHANGE_DELTA_IN_DAY * MAP_SYNC_TIME) / (24 * TURNS_IN_HOUR)

PLACE_STABILITY_UNIT = float(0.1) # базовая единица изменения стабильности

# считаем что штраф от одной записи в Книге Судеб должен восстанавливаться за неделю
PLACE_STABILITY_RECOVER_SPEED = float(PLACE_STABILITY_UNIT / (7*24)) # стабильности в час

PLACE_STABILITY_MAX_PRODUCTION_PENALTY = float(-PLACE_GOODS_BONUS * 2)
PLACE_STABILITY_MAX_SAFETY_PENALTY = float(-0.25)
PLACE_STABILITY_MAX_TRANSPORT_PENALTY = h.speed_from_safety(PLACE_STABILITY_MAX_SAFETY_PENALTY, BATTLES_PER_TURN)
PLACE_STABILITY_MAX_FREEDOM_PENALTY = -PLACE_STABILITY_MAX_TRANSPORT_PENALTY
PLACE_STABILITY_MAX_CULTURE_PENALTY = -1.0

PLACE_STABILITY_PENALTY_FOR_MASTER = float(-0.15)
PLACE_STABILITY_PENALTY_FOR_RACES = float(-0.5) # штраф к стабильности за 100% разницы в давлении рас
PLACE_STABILITY_PENALTY_FOR_SPECIALIZATION = float(-0.5) # штраф за полное несоответствие специализации (когда 0 очков)


# считаем на сколько условных единиц бонусов от Мастеров влияет нулевая стабильность
_STABILITY_PERSONS_POINTS = (abs(PLACE_STABILITY_MAX_PRODUCTION_PENALTY) / PLACE_GOODS_FROM_BEST_PERSON +
                             abs(PLACE_STABILITY_MAX_SAFETY_PENALTY) / PLACE_SAFETY_FROM_BEST_PERSON +
                             abs(PLACE_STABILITY_MAX_TRANSPORT_PENALTY) / PLACE_TRANSPORT_FROM_BEST_PERSON +
                             -abs(PLACE_STABILITY_MAX_FREEDOM_PENALTY) / PLACE_FREEDOM_FROM_BEST_PERSON + # на свободу отсутствие стабильности влияет положительно
                             abs(PLACE_STABILITY_MAX_CULTURE_PENALTY) / PLACE_CULTURE_FROM_BEST_PERSON)

# считаем максимальную стабильность от Мастера
PLACE_STABILITY_FROM_BEST_PERSON = float(1.0 / _STABILITY_PERSONS_POINTS)

WHILD_TRANSPORT_PENALTY = float(0.1) # штраф к скорости в диких землях и на фронтире
TRANSPORT_FROM_PLACE_SIZE_PENALTY = float(0.05) # штраф к скорости от размера города

PLACE_HABITS_CHANGE_SPEED_MAXIMUM = float(10)
PLACE_HABITS_CHANGE_SPEED_MAXIMUM_PENALTY = float(10)
PLACE_HABITS_EVENT_PROBABILITY = float(0.025)

PLACE_JOB_EFFECT_FRACTION = float(0.2)

JOB_PRODUCTION_BONUS = int(PLACE_GOODS_BONUS * PLACE_JOB_EFFECT_FRACTION)
JOB_SAFETY_BONUS = float(PLACE_SAFETY_FROM_BEST_PERSON * PLACE_JOB_EFFECT_FRACTION)
JOB_TRANSPORT_BONUS = float(PLACE_TRANSPORT_FROM_BEST_PERSON * PLACE_JOB_EFFECT_FRACTION)
JOB_FREEDOM_BONUS = float(PLACE_FREEDOM_FROM_BEST_PERSON * PLACE_JOB_EFFECT_FRACTION)
JOB_STABILITY_BONUS = float(PLACE_STABILITY_UNIT * PLACE_JOB_EFFECT_FRACTION)
JOB_CULTURE_BONUS = float(PLACE_CULTURE_FROM_BEST_PERSON * PLACE_JOB_EFFECT_FRACTION)

###########################
# мастера
###########################

PERSON_MOVE_DELAY_IN_WEEKS = int(2)
PERSON_MOVE_DELAY = int(TURNS_IN_HOUR * 24 * 7 * PERSON_MOVE_DELAY_IN_WEEKS) # минимальная задержка между переездами Мастера

PERSON_SOCIAL_CONNECTIONS_LIMIT = int(3)

PERSON_SOCIAL_CONNECTIONS_MIN_LIVE_TIME_IN_WEEKS = int(2)
PERSON_SOCIAL_CONNECTIONS_MIN_LIVE_TIME = int(TURNS_IN_HOUR * 24 * 7 * PERSON_SOCIAL_CONNECTIONS_MIN_LIVE_TIME_IN_WEEKS)

PERSON_SOCIAL_CONNECTIONS_POWER_BONUS = float(0.1)

###########################
# здания
###########################

BUILDING_MASTERY_BONUS = float(0.15)

BUILDING_POSITION_RADIUS = int(2)

# на починку зданий игроки тратят энергию
# желательно, чтобы для единственного здания в городе эффект единичной траты энергии был заметен

BUILDING_FULL_DESTRUCTION_TIME = int(2*7*24) # in hours
BUILDING_AMORTIZATION_SPEED = float(1.0 / BUILDING_FULL_DESTRUCTION_TIME) # percents/hour

# единственное здание города  может поддерживаться одним человеком при условии траты всей энергии
BUILDING_FULL_REPAIR_ENERGY_COST = int(BUILDING_FULL_DESTRUCTION_TIME * ANGEL_ENERGY_REGENERATION_AMAUNT * ANGEL_ENERGY_REGENERATION_PERIOD / TURNS_IN_HOUR)

BUILDING_AMORTIZATION_MODIFIER = float(1.5) # цена ремонта здания зависит от количества зданий в городе и равно <цена>*BULDING_AMORTIZATION_MODIFIER^<количество зданий - 1>
BUILDING_WORKERS_ENERGY_COST = int(3) # цена вызова одного рабочего

BUILDING_PERSON_POWER_BONUS = float(0.25)
BUILDING_TERRAIN_POWER_MULTIPLIER = float(0.5) # building terrain power is percent from city power

###########################
# Карты
###########################

CARDS_HELP_COUNT_TO_NEW_CARD = int(1.5 * ANGEL_ENERGY_IN_DAY / ANGEL_HELP_COST)
CARDS_COMBINE_TO_UP_RARITY = 3


###########################
# Спутники
###########################

# под средним спутником понимается спутник со
# - средним здоровьем
# - средней самоотверженностью
# - средней слаженностью

# рост слаженности огранизуется так, чтобы она росла сначала быстро, потом ооооооочень долго
# в качестве опыта идёт 1 выполненного задания
# для получения слаженности N требуется N опыта

COMPANIONS_MIN_COHERENCE = int(0)   # минимальный уровень слаженности
COMPANIONS_MAX_COHERENCE = int(100) # максимальный уровень слаженности

# опыта к слаженности за выполненный квест
# подбирается так, чтобы слаженность росла до максимума примерно за 9 месяцев
_QUESTS_REQUIED = (9*30*24*60*60) / (TURNS_IN_QUEST * TURN_DELTA)
COMPANIONS_COHERENCE_EXP_PER_QUEST = int(((1+100)*100/2) / _QUESTS_REQUIED)

COMPANIONS_MEDIUM_COHERENCE = float(COMPANIONS_MIN_COHERENCE + COMPANIONS_MAX_COHERENCE) / 2

COMPANIONS_MIN_HEALTH = int(300) # минимальное максимальное здоровье спутника
COMPANIONS_MAX_HEALTH = int(700) # максимальное максимальное здоровье спутника

COMPANIONS_MEDIUM_HEALTH = float(COMPANIONS_MIN_HEALTH + COMPANIONS_MAX_HEALTH) / 2

_COMPANIONS_MEDIUM_LIFETYME = int(12) # ожидаемое время жизни среднего спутника со средним здоровьем без лечения в днях

# дельты мультипликатора вероятности блока для
COMPANIONS_BLOCK_MULTIPLIER_COHERENCE_DELTA = float(0.2) # слаженность (от среднего)
COMPANIONS_BLOCK_MULTIPLIER_COMPANION_DEDICATION_DELTA = float(0.2) # самоотверженности спутника
COMPANIONS_BLOCK_MULTIPLIER_HERO_DEDICATION_DELTA = float(0.2) # самоотверженность героя

COMPANIONS_HABITS_DELTA = float(0.5) # дельта изменения черт от среднего в зависимости от предпочтения

COMPANIONS_DEFEND_PROBABILITY = float(COMPANIONS_DEFENDS_IN_BATTLE) / (BATTLE_LENGTH / 2)


COMPANIONS_HEALS_IN_HOUR = float(1.5) # частота действия уход за спутником в час

COMPANIONS_HEALTH_PER_HEAL = int(2) # лечение спутника за одно действие ухода за спутником
COMPANIONS_DAMAGE_PER_WOUND = int(10) # урон спутнику за ранение

# частота ранений героя
COMPANIONS_WOUNDS_IN_HOUR_FROM_HEAL = COMPANIONS_HEALS_IN_HOUR * COMPANIONS_HEALTH_PER_HEAL / COMPANIONS_DAMAGE_PER_WOUND
COMPANIONS_WOUNDS_IN_HOUR_FROM_WOUNDS = float(COMPANIONS_MEDIUM_HEALTH) / COMPANIONS_DAMAGE_PER_WOUND / (_COMPANIONS_MEDIUM_LIFETYME * 24)
COMPANIONS_WOUNDS_IN_HOUR = COMPANIONS_WOUNDS_IN_HOUR_FROM_WOUNDS + COMPANIONS_WOUNDS_IN_HOUR_FROM_HEAL

COMPANIONS_WOUND_ON_DEFEND_PROBABILITY_FROM_WOUNDS =  COMPANIONS_WOUNDS_IN_HOUR_FROM_WOUNDS / (BATTLES_PER_HOUR * COMPANIONS_DEFENDS_IN_BATTLE)

# величины лечения здоровья спутника за одну помощь
COMPANIONS_HEAL_AMOUNT = int(20)
COMPANIONS_HEAL_CRIT_AMOUNT = COMPANIONS_HEAL_AMOUNT * 2

# вероятность того, что спутник использует способность во время боя
# на столько же должны увеличивать инициативу особенности спутника с боевыми способностями
COMPANIONS_BATTLE_STRIKE_PROBABILITY = float(0.05)


COMPANIONS_EXP_PER_MOVE_GET_EXP = int(1) # получаемый героем опыт за одно «действие получения опыта во время движения героя»

# количество получений опыта от спутника в час
COMPANIONS_GET_EXP_MOVE_EVENTS_PER_HOUR = float(EXP_PER_HOUR * COMPANIONS_BONUS_EXP_FRACTION) / COMPANIONS_EXP_PER_MOVE_GET_EXP
COMPANIONS_EXP_PER_MOVE_PROBABILITY = COMPANIONS_GET_EXP_MOVE_EVENTS_PER_HOUR / MOVE_TURNS_IN_HOUR

# количество опыта за каждое лечение спутника (при наличии нужной способности)
COMPANIONS_EXP_PER_HEAL = int(EXP_PER_HOUR * COMPANIONS_BONUS_EXP_FRACTION / COMPANIONS_HEALS_IN_HOUR)

COMPANIONS_HEAL_BONUS = float(0.25) # доля отлечиваемого способностями спутников или героя

# количество вылеченного здоровья в час для спутников с лечебной способностью (рассчитывается исходя только из ранений, не компенсирующих лечение действием ухода)
COMPANIONS_REGEN_PER_HOUR = COMPANIONS_WOUNDS_IN_HOUR_FROM_WOUNDS * COMPANIONS_DAMAGE_PER_WOUND * COMPANIONS_HEAL_BONUS

COMPANIONS_EATEN_CORPSES_HEAL_AMOUNT = int(1)
COMPANIONS_REGEN_ON_HEAL_AMOUNT = int(1)
COMPANIONS_REGEN_BY_HERO = int(1)
COMPANIONS_REGEN_BY_MONEY_SPEND = int(1)

COMPANIONS_EATEN_CORPSES_PER_BATTLE = float(COMPANIONS_REGEN_PER_HOUR) / BATTLES_PER_HOUR / COMPANIONS_EATEN_CORPSES_HEAL_AMOUNT
COMPANIONS_REGEN_ON_HEAL_PER_HEAL = float(COMPANIONS_REGEN_PER_HOUR) / COMPANIONS_HEALS_IN_HOUR / COMPANIONS_REGEN_ON_HEAL_AMOUNT
COMPANIONS_HERO_REGEN_ON_HEAL_PER_HEAL = float(COMPANIONS_REGEN_PER_HOUR) / COMPANIONS_HEALS_IN_HOUR / COMPANIONS_REGEN_BY_HERO

COMPANIONS_GIVE_COMPANION_AFTER = int(24) # выдавать спутника герою без спутника примерно раз в N часов

COMPANIONS_LEAVE_IN_PLACE = float(1.0 / 20) # вероятность того, что нелюдимый спутник покинет героя в городе

COMPANIONS_BONUS_DAMAGE_PROBABILITY = float(0.25) # вероятность спутника получить дополнительный урон


##############################
# Bills
##############################

PLACE_MAX_BILLS_NUMBER = int(3)

FREE_ACCOUNT_MAX_ACTIVE_BILLS = int(1)
PREMIUM_ACCOUNT_MAX_ACTIVE_BILLS = int(4)
