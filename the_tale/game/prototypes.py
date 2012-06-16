# coding: utf-8
from collections import namedtuple

from game.balance import formulas as f

from game.models import Time

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

    def __init__(self, model):
        self.model = model

    @property
    def game_time(self): return GameTime(*f.turns_to_game_time(self.turn_number))

    @property
    def turn_number(self): return self.model.turn_number

    @classmethod
    def get_current_time(cls):
        try:
            return TimePrototype(model=Time.objects.all()[0])
        except IndexError:
            return TimePrototype.create()


    def increment_turn(self):
        self.model.turn_number += 1

    def save(self):
        self.model.save()

    @classmethod
    def create(cls):
        return cls(model=Time.objects.create())

    def ui_info(self):
        game_time = self.game_time
        return { 'number': self.turn_number,
                 'verbose_date': game_time.verbose_date,
                 'verbose_time': game_time.verbose_time }
