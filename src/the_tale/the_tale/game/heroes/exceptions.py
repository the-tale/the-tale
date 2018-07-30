
import smart_imports

smart_imports.all()


class HeroError(utils_exceptions.TheTaleError):
    MSG = 'hero error'


class HealHeroForNegativeValueError(HeroError):
    MSG = 'try to heal hero to negative value'


class UnkwnownAchievementTypeError(HeroError):
    MSG = 'unknown achievement type: %(achievement_type)r'


class UnknownMoneySourceError(HeroError):
    MSG = 'unknown money source %(source)r'


class HelpCountBelowZero(HeroError):
    MSG = 'try decrease help count below zero (current_value: %(current_value)d, delta: %(delta)d)'


class EquipmentError(HeroError):
    pass


class SlotAlreadyBusy(EquipmentError):
    MSG = 'slot "{slot}" for equipment has already busy'


class UnknownSlot(EquipmentError):
    MSG = 'unknown slot "{slot}"'
