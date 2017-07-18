

from the_tale.game.balance import constants as c

from . import exceptions


class CardsInfo:
    __slots__ = ('_hero', '_help_count', '_premium_help_count')

    def __init__(self):
        self._help_count = 0
        self._premium_help_count = 0

    @property
    def help_count(self): return self._help_count

    def serialize(self):
        return {'help_count': self._help_count,
                'premium_help_count': self._premium_help_count}

    @classmethod
    def deserialize(cls, data):
        obj = cls()
        obj._help_count = data.get('help_count', 0)
        obj._premium_help_count = data.get('premium_help_count', 0)
        return obj

    def ui_info(self):
        return {'help_count': self._help_count,
                'help_barrier': c.CARDS_HELP_COUNT_TO_NEW_CARD }

    @classmethod
    def ui_info_null(self):
        return {'help_count': 0,
                'help_barrier': c.CARDS_HELP_COUNT_TO_NEW_CARD }

    def change_help_count(self, delta):
        if self._help_count + delta < 0:
            raise exceptions.HelpCountBelowZero(current_value=self._help_count, delta=delta)

        self._help_count += delta

        if delta > 0 and self._hero.is_premium:
            self._premium_help_count += delta

        if delta < 0:
            self._premium_help_count = min(self._help_count, self._premium_help_count)


    def is_next_card_premium(self):
        return self._help_count != 0 and self._help_count == self._premium_help_count
