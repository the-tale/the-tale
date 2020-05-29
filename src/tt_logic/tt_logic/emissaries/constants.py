
import math

from typing import List

from tt_logic.clans import constants as clans_constants


MAXIMUM_HEALTH: int = 7000
MAXIMUM_HEALTH_DELTA: int = 2000

NORMAL_DAMAGE_TO_HEALTH: int = 1000
DAMAGE_TO_HEALTH_DELTA: int = 500

# в час
HEALTH_REGENERATION_MIN: int = int(math.ceil(0.25 * NORMAL_DAMAGE_TO_HEALTH / 24))
HEALTH_REGENERATION_MAX: int = int(math.ceil(1.5 * NORMAL_DAMAGE_TO_HEALTH / 24))

EMISSARY_POWER_HISTORY_WEEKS: int = 4  # количество недель, которое хранится влияние
EMISSARY_POWER_HISTORY_LENGTH: int = EMISSARY_POWER_HISTORY_WEEKS * 7 * 24  # в часах

EMISSARY_POWER_RECALCULATE_STEPS: float = EMISSARY_POWER_HISTORY_LENGTH
EMISSARY_POWER_REDUCE_FRACTION: float = math.pow(0.01, 1.0 / EMISSARY_POWER_RECALCULATE_STEPS)

INITIAL_ATTRIBUTE_VALUE: int = 0

ATRIBUTE_MAXIMUM_DELTA: int = 2500

NORMAL_ATTRIBUTE_MAXIMUM: int = 10000

MAXIMUM_ATTRIBUTE_MAXIMUM: int = NORMAL_ATTRIBUTE_MAXIMUM + ATRIBUTE_MAXIMUM_DELTA

# предполагаем, что значение аттрибута прирастает каждый день при его использовании в мероприятии
# предполагаем, что до максимума аттрибут должен качаться примерно EXPECTED_LEVELING_TIME дней

EXPECTED_LEVELING_TIME: int = 1 * 365

_ATTRIBUT_INCREMENT_DELTA: float = ((NORMAL_ATTRIBUTE_MAXIMUM - INITIAL_ATTRIBUTE_VALUE) /
                                    (clans_constants.SIMULTANEOUS_EMISSARY_EVENTS * EXPECTED_LEVELING_TIME))
ATTRIBUT_INCREMENT_DELTA: int = int(math.ceil(_ATTRIBUT_INCREMENT_DELTA))

ATTRIBUT_INCREMENT_BUFF: int = 7

BUFFED_ATTRIBUT_INCREMENT_DELTA: int  = ATTRIBUT_INCREMENT_DELTA + ATTRIBUT_INCREMENT_BUFF
DEBUFFED_ATTRIBUT_INCREMENT_DELTA: int = ATTRIBUT_INCREMENT_DELTA - ATTRIBUT_INCREMENT_BUFF


QUEST_POWER_BONUS: float = 0.5

QUEST_EXPERIENCE_BUFF: float = 2.0
QUEST_EXPERIENCE_DEBUFF: float = 0.7

POSITIVE_TRAITS_NUMBER: int = 3
NEGATIVE_TRAITS_NUMBER: int = 2

EVENT_POWER_FRACTION: float = 0.5  # от расчётного дневного влияния

EVENT_EXPERIENCE_BUFF: float = 0.25
EVENT_EXPERIENCE_DEBUFF: float = 0.25

# в час
MIN_EXPERIENCE_PER_EVENT: int = int(math.ceil(clans_constants.EXPERIENCE_PER_EVENT / 24 / 2))
MAX_EXPERIENCE_PER_EVENT: int = int(math.ceil(clans_constants.EXPERIENCE_PER_EVENT / 24 * 2))

# в час
MIN_ACTION_POINTS_PER_EVENT: int = int(0.5 * clans_constants.INITIAL_POINTS_IN_DAY // 24)
MAX_ACTION_POINTS_PER_EVENT: int = int(1.5 * clans_constants.INITIAL_POINTS_IN_DAY // 24)


STANDART_LIMITED_TASK_POINTS_MINIMUM: int = int(math.ceil(clans_constants.FIGHTERS_TO_EMISSARY / 2))
STANDART_LIMITED_TASK_POINTS_MAXIMUM: int = 3 * clans_constants.FIGHTERS_TO_EMISSARY

EVENT_CURRENCY_MULTIPLIER: int = 1000

PLACE_LEADERS_NUMBER: int = 3

RACE_PRESSURE_MODIFIER_MIN: float = 0.25
RACE_PRESSURE_MODIFIER_MAX: float = 2.00

# время которое должен качаться эмиссар, чтобы члены его клана могли выполнять задания для эмиссаров других гильдий
# считаем, что время лучше всего показывает вклад гильдии в развитие эмиссара, поэтому ориентируемя на него
TIME_FOR_PARTICIPATE_IN_PVP: int = 30  # дней

# также необходимо учитывать, что разные мероприятия по-разному прокачивают эмиссара
EXPECTED_ATTRIBUTES_INCREMENT_FROM_EVENT: int = 2 * ATTRIBUT_INCREMENT_DELTA

ATTRIBUTES_FOR_PARTICIPATE_IN_PVP: int = (TIME_FOR_PARTICIPATE_IN_PVP *
                                          clans_constants.SIMULTANEOUS_EMISSARY_EVENTS *
                                          ATTRIBUT_INCREMENT_DELTA)

TASK_BOARD_PLACES_NUMBER: int = 10

_PROTECTORAT_BONUSES_FOR_LEVEL: List[float] = [0,
                                               0.50,
                                               0.25,
                                               0.20,
                                               0.20,
                                               0.20,
                                               0.15,
                                               0.15,
                                               0.15,
                                               0.10,
                                               0.10]


PROTECTORAT_BONUSES: List[float] = [round(sum(_PROTECTORAT_BONUSES_FOR_LEVEL[:i+1]), 2)
                                    for i in range(len(_PROTECTORAT_BONUSES_FOR_LEVEL))]

PLACE_EVENT_MIN_EFFECT_POWER: float = 0.25
PLACE_EVENT_MAX_EFFECT_POWER: float = 1.25
