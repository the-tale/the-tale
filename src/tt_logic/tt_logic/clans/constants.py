
import math

from tt_logic.common import series

# Скорость прихода очков действий гильдии расчитываем опираясь на желаемую скорость получения новых эмиссаров гильдиями
# При условии, что активные эмиссары постоянно заняты одним мероприятием

EXPECTED_EVENT_LENGTH = int(7)  # дней

EMISSARY_RECEIVE_PERIOD_FOR_NEW_CLAN = int(21)  # дней
EXPECTED_EMISSARY_RECEIVE_PERIOD_FOR_TOP_CLAN = int(7)  # дней

SIMULTANEOUS_EMISSARY_EVENTS = int(2)

INITIAL_POINTS_IN_DAY = int(1000)

PRICE_START_EVENT = INITIAL_POINTS_IN_DAY
PRICE_CREATE_EMISSARY = int(EMISSARY_RECEIVE_PERIOD_FOR_NEW_CLAN * (INITIAL_POINTS_IN_DAY - 1 * PRICE_START_EVENT  / EXPECTED_EVENT_LENGTH))
PRICE_MOVE_EMISSARY = PRICE_START_EVENT
PRICE_DISMISS_EMISSARY = PRICE_START_EVENT

# топовая карта Судьбы должна давать незначительную часть очков для инициации действия.
# назначение карт — добавить недостающие очки действий, а не стать главным источником получения очков
TOP_CARD_POINTS_BONUS = int(0.1 * PRICE_START_EVENT)

INITIAL_MEMBERS_MAXIMUM = int(5)
INITIAL_EMISSARY_MAXIMUM = int(2)
INITIAL_FREE_QUESTS_MAXIMUM = int(2)  # в день
INITIAL_POINTS_GAIN = PRICE_CREATE_EMISSARY // EMISSARY_RECEIVE_PERIOD_FOR_NEW_CLAN
INITIAL_POINTS = PRICE_CREATE_EMISSARY + PRICE_START_EVENT
INITIAL_FREE_QUESTS = INITIAL_FREE_QUESTS_MAXIMUM
INITIAL_EMISSARY_POWER = int(1000)

MAXIMUM_POINTS_GAIN = PRICE_CREATE_EMISSARY // EXPECTED_EMISSARY_RECEIVE_PERIOD_FOR_TOP_CLAN
MAXIMUM_EMISSARIES = int(10)

# прикидываем исходя из одного эмиссара на 10 игроков
MAXIMUM_MEMBERS = int(100)

MAXIMUM_FREE_QUESTS = int(10)

# самая большая трата для гильдии — покупка эмиссара, нет смысла копить очки действий больше, чем на две покупки
MAXIMUM_POINTS = 2 * PRICE_CREATE_EMISSARY

# Прокачка количества эмиссаров и скорости прироста очков гильдии расчитывается исходя из:
# - ожидаемого суммарного времени прокачки гильдии до максимума
# - возрастания времени прокачки каждого следующего уровня
# - предположения, что на протяжении этого времени скорость получения опыта гильдией растёт пропорционально прошедшему времени
# - предположения, что каждый эмиссар постоянно имеет активным все мероприятия
#
# Для удобства расчёта опыт считается в днях мероприятий, итоговые числа будут получены домножением на удобную константу
# Прокачку количества членов гильдии сознательно игнорируем в этом плане.
# Считаем, что гильдии найдут способ опережающей прокачки и избыток опыта будут тратить на увеличение своего размера.

EMISSARY_MAXIMUM_LEVEL_STEPS = MAXIMUM_EMISSARIES - INITIAL_EMISSARY_MAXIMUM
POINTS_GAIN_LEVEL_STEPS = int(20)
MEMBERS_MAXIMUM_LEVEL_STEPS = MAXIMUM_MEMBERS - INITIAL_MEMBERS_MAXIMUM
FREE_QUESTS_MAXIMUM_LEVEL_STEPS = MAXIMUM_FREE_QUESTS - INITIAL_FREE_QUESTS_MAXIMUM

EXPECTED_LEVELING_TIME = int(5 * 365)  # дней

POINTS_GAIN_INCREMENT_ON_LEVEL_UP = int((MAXIMUM_POINTS_GAIN - INITIAL_POINTS_GAIN) / POINTS_GAIN_LEVEL_STEPS)

EXPERIENCE_PER_EVENT = int(100)  # в день

EXPERIENCE_IN_DAY_ON_START = SIMULTANEOUS_EMISSARY_EVENTS * INITIAL_EMISSARY_MAXIMUM * EXPERIENCE_PER_EVENT
EXPERIENCE_IN_DAY_ON_END = SIMULTANEOUS_EMISSARY_EVENTS * MAXIMUM_EMISSARIES * EXPERIENCE_PER_EVENT


MINIMUM_TIME_TO_EMISSARY_LEVEL = int(7)  # дней
MINIMUM_TIME_TO_MEMBERS_LEVEL = int(3)  # дней


_emissary_generator = series.ExponentialSeriesGenerator(base=MINIMUM_TIME_TO_EMISSARY_LEVEL)
_members_generator = series.ExponentialSeriesGenerator(base=MINIMUM_TIME_TO_MEMBERS_LEVEL)


EMISSARY_MAXIMUM_LEVELS_TIME = _emissary_generator.series(n=EMISSARY_MAXIMUM_LEVEL_STEPS, border=EXPECTED_LEVELING_TIME / 3)
POINTS_GAIN_LEVELS_TIME = _emissary_generator.series(n=POINTS_GAIN_LEVEL_STEPS, border=EXPECTED_LEVELING_TIME / 3)
FREE_QUESTS_MAXIMUM_LEVELS_TIME = _emissary_generator.series(n=FREE_QUESTS_MAXIMUM_LEVEL_STEPS, border=EXPECTED_LEVELING_TIME / 3)

MEMBERS_MAXIMUM_LEVELS_TIME = _members_generator.series(n=MEMBERS_MAXIMUM_LEVEL_STEPS, border=EXPECTED_LEVELING_TIME)


def _experience_levels(time_series):
    return series.time_series_to_values(time_series=time_series,
                                        start_speed=EXPERIENCE_IN_DAY_ON_START,
                                        end_speed=EXPERIENCE_IN_DAY_ON_END,
                                        rounder=lambda value: int(round(value, -2)))


EMISSARY_MEXIMUM_LEVELS_EXPERIENCE = _experience_levels(EMISSARY_MAXIMUM_LEVELS_TIME)
POINTS_GAIN_LEVELS_EXPERIENCE = _experience_levels(POINTS_GAIN_LEVELS_TIME)
FREE_QUESTS_MAXIMUM_LEVELS_EXPERIENCE = _experience_levels(FREE_QUESTS_MAXIMUM_LEVELS_TIME)
MEMBERS_MAXIMUM_LEVELS_EXPERIENCE = _experience_levels(MEMBERS_MAXIMUM_LEVELS_TIME)

EMISSARY_POWER_HISTORY_WEEKS = int(4)  # количество недель, которое хранится влияние
EMISSARY_POWER_HISTORY_LENGTH = int(EMISSARY_POWER_HISTORY_WEEKS * 7 * 24)  # в часах

EMISSARY_POWER_RECALCULATE_STEPS = float(EMISSARY_POWER_HISTORY_LENGTH)
EMISSARY_POWER_REDUCE_FRACTION = float(math.pow(0.01, 1.0 / EMISSARY_POWER_RECALCULATE_STEPS))

MAXIMUM_EMISSARY_HEALTH = int(7)
