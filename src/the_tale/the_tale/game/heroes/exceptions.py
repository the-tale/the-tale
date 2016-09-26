# coding: utf-8

from the_tale.common.utils.exceptions import TheTaleError


class HeroError(TheTaleError):
    MSG = 'hero error'


class HealHeroForNegativeValueError(HeroError):
    MSG = 'try to heal hero to negative value'

class UnkwnownAchievementTypeError(HeroError):
    MSG = 'unknown achievement type: %(achievement_type)r'


class UnknownMoneySourceError(HeroError):
    MSG = 'unknown money source %(source)r'
