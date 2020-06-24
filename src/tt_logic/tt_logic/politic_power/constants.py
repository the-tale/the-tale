
import math

from tt_logic.cards import constants as cards_constants

from the_tale.game.balance import constants as tale_constants


# базовое количество влияния за квест минимального ранга
POWER_PER_QUEST: int = 100

# длительность жизни влияния
POWER_HISTORY_WEEKS: int = 6  # недель
POWER_HISTORY_LENGTH: int = int(POWER_HISTORY_WEEKS * 7 * 24 * tale_constants.TURNS_IN_HOUR)  # в ходах

POWER_RECALCULATE_STEPS: float = POWER_HISTORY_LENGTH / tale_constants.MAP_SYNC_TIME
POWER_REDUCE_FRACTION: float = math.pow(0.01, 1.0 / POWER_RECALCULATE_STEPS)

######################################
# бонусы к влиянию для всех источников
######################################

# принципы определения размеров бонусов:
#
# - бонусы суммируются
# - бонусы бьются на группы по ожидаемой силе их влияния
# - величины бонусов в одной группе могут различаться, но сеильно
# - влияние, исходящее чисто от героя, должно составлять существенную часть общего влияния (половина или больше)
# - если не указано обратное, модификаторы задают максимально возможное значение

# группы:
#
# главные:
# - героя: способности
#
# основные:
# - город: свобода
# - Мастер: здание
# - герой: спутник
#
# вспомогательные:
# - Мастер: характер
# - герой: артефакты
# - герой: могущество
# - эмиссар: особенности

# главная группа
MODIFIER_HERO_ABILITIES: float = 3.0

# основная группа

# свобода городов сейчас находится большей частью в промежутке от [-1, 1]
# если это изменится, надо будет пересмотреть коофициент коерсии

EXPECTED_PLACE_FREEDOM_MAXIMUM: float = 1.0

MODIFIER_PLACE_FREEDOM: float = 1.5
MODIFIER_PERSON_BUILDING: float = 1.0
MODIFIER_HERO_COMPANION: float = 1.5

# вспомогательная группа

MODIFIER_PERSON_CHARACTER: float = 0.5

MODIFIER_HERO_ARTIFACTS_RARE: float = 0.2
MODIFIER_HERO_ARTIFACTS_EPIC: float = 0.6

# для расчёта влияния от могущества см. .formulas.might_to_power
# поскольку могущество зарабатывается сложно и не должно давать большой бонус
# при аггрегируемых расчётах его можно игнорировать
# MODIFIER_HERO_MIGHT

MODIFIER_EMISSARY: float = 0.5

SOCIAL_CONNECTIONS_POWER_FRACTION: float = 0.1

# ожидаемое количество влияния от задания, после которого рост влиния от ранга заметен не сильно
# выбирается на глаз
# подробнее см. в тестах
EXPECTED_STABLE_BASE_QUEST_POWER: int = 600

EXPECTED_POWER_FROM_POLITIC: float = (1 + MODIFIER_HERO_ABILITIES + MODIFIER_HERO_COMPANION + MODIFIER_HERO_ARTIFACTS_EPIC)

MEDIUM_QUEST_POWER: int  = int(math.ceil(EXPECTED_STABLE_BASE_QUEST_POWER * EXPECTED_POWER_FROM_POLITIC))

CARD_MAX_POWER: int = EXPECTED_STABLE_BASE_QUEST_POWER * cards_constants.LEVEL_MULTIPLIERS[2]
