
import math

from . import constants as c


def base_quest_power(quest_rung: int) -> int:
    return int(math.ceil(c.POWER_PER_QUEST * (1 + math.log(quest_rung, 2))))


def might_to_power(might: float) -> float:
    if might < 1:
        return 0

    return (math.log(might, 10) / 3)


def power_modifier_from_freedom(freedom: float) -> float:
    return freedom / c.EXPECTED_PLACE_FREEDOM_MAXIMUM * c.MODIFIER_PLACE_FREEDOM
