
import datetime

from dext.settings import settings

from utg import words as utg_words
from utg.relations import WORD_TYPE

import tt_calendar


TURN_SETTINGS_KEY = 'turn number'


def number():
    return int(settings.get(TURN_SETTINGS_KEY, 0))


def increment(delta=1):
    set(number() + delta)


def set(turn):
    settings[TURN_SETTINGS_KEY] = str(turn)


def game_datetime(turn=None):
    if turn is None:
        turn = number()

    return tt_calendar.converter.from_turns(turn)


def ui_info(turn=None):
    if turn is None:
        turn = number()

    turn_datetime = game_datetime(turn)

    return {'number': turn,
            'verbose_date': turn_datetime.date.verbose_full(),
            'verbose_time': turn_datetime.time.verbose()}


class LinguisticsDate(object):
    __slots__ = ('date', )

    def __init__(self, date):
        self.date = date

    @property
    def utg_name_form(self):
        return utg_words.WordForm(utg_words.Word(type=WORD_TYPE.TEXT, forms=(self.date.verbose_full(),)))

    def linguistics_restrictions(self, now=None):
        from the_tale.linguistics import storage
        from the_tale.linguistics.relations import TEMPLATE_RESTRICTION_GROUP

        restrictions = []

        get_restriction = storage.restrictions_storage.get_restriction

        for real_feast in tt_calendar.actual_real_feasts(now=now):
            restrictions.append(get_restriction(TEMPLATE_RESTRICTION_GROUP.REAL_FEAST, real_feast.value).id)

        for calendar_date in tt_calendar.actual_dates(self.date, tt_calendar.DATE):
            restrictions.append(get_restriction(TEMPLATE_RESTRICTION_GROUP.CALENDAR_DATE, calendar_date.value).id)

        for physics_date in tt_calendar.actual_dates(self.date, tt_calendar.PHYSICS_DATE):
            restrictions.append(get_restriction(TEMPLATE_RESTRICTION_GROUP.PHYSICS_DATE, physics_date.value).id)

        restrictions.append(get_restriction(TEMPLATE_RESTRICTION_GROUP.MONTH, self.date.month).id)
        restrictions.append(get_restriction(TEMPLATE_RESTRICTION_GROUP.QUINT, self.date.quint).id)
        restrictions.append(get_restriction(TEMPLATE_RESTRICTION_GROUP.QUINT_DAY, self.date.quint_day).id)

        restrictions.append(get_restriction(TEMPLATE_RESTRICTION_GROUP.DAY_TYPE, tt_calendar.day_type(self.date).value).id)

        return restrictions


class LinguisticsTime(object):
    __slots__ = ('time', )

    def __init__(self, time):
        self.time = time

    @property
    def utg_name_form(self):
        return utg_words.WordForm(utg_words.Word(type=WORD_TYPE.TEXT, forms=(self.time.verbose(),)))

    def linguistics_restrictions(self, now=None):
        from the_tale.linguistics import storage
        from the_tale.linguistics.relations import TEMPLATE_RESTRICTION_GROUP

        restrictions = []

        get_restriction = storage.restrictions_storage.get_restriction

        for day_time in tt_calendar.day_times(self.time):
            restrictions.append(get_restriction(TEMPLATE_RESTRICTION_GROUP.DAY_TIME, day_time.value).id)

        return restrictions


def linguistics_date(turn=None):
    return LinguisticsDate(game_datetime(turn).date)


def linguistics_time(turn=None):
    return LinguisticsTime(game_datetime(turn).time)
