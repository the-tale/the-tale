# coding: utf-8

from dext.settings import settings

from collections import namedtuple

from game.balance import formulas as f

class GameTime(namedtuple('GameTimeTuple', ('year', 'month', 'day', 'hour', 'minute', 'second'))):

    MONTH_NAMES = {1: u'холодного месяца',
                   2: u'сырого месяца',
                   3: u'жаркого месяца',
                   4: u'сухого месяца'}

    @classmethod
    def create_from_turn(cls, turn_number):
        return cls(*f.turns_to_game_time(turn_number))

    @property
    def verbose_date(self):
        return u'%(day)d день %(month)s %(year)d года' % {'day': self.day,
                                                          'month': self.MONTH_NAMES[self.month],
                                                          'year': self.year}
    @property
    def verbose_time(self):
        return u'%(hour).2d:%(minute).2d' % {'hour': self.hour,
                                             'minute': self.minute}


class TimePrototype(object):

    def __init__(self, turn_number):
        self.turn_number = turn_number

    @property
    def game_time(self): return GameTime(*f.turns_to_game_time(self.turn_number))

    @classmethod
    def get_current_time(cls):
        return cls(turn_number=cls.get_current_turn_number())

    @classmethod
    def get_current_turn_number(cls):
        if 'turn number' not in settings:
            settings['turn number'] = '0'
        return int(settings['turn number'])

    def increment_turn(self):
        self.turn_number += 1

    def save(self):
        settings['turn number'] = str(self.turn_number)

    def ui_info(self):
        game_time = self.game_time
        return { 'number': self.turn_number,
                 'verbose_date': game_time.verbose_date,
                 'verbose_time': game_time.verbose_time }
