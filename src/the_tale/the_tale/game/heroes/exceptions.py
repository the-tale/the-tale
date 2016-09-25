# coding: utf-8

from the_tale.common.utils.exceptions import TheTaleError


class HeroError(TheTaleError):
    MSG = u'hero error'


class HealHeroForNegativeValueError(HeroError):
    MSG = u'try to heal hero to negative value'

class UnkwnownAchievementTypeError(HeroError):
    MSG = u'unknown achievement type: %(achievement_type)r'


class UnknownMoneySourceError(HeroError):
    MSG = u'unknown money source %(source)r'
