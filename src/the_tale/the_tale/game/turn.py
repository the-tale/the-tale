
import smart_imports

smart_imports.all()


TURN_SETTINGS_KEY = 'turn number'


def number():
    return int(dext_settings.settings.get(TURN_SETTINGS_KEY, 0))


def increment(delta=1):
    set(number() + delta)


def set(turn):
    dext_settings.settings[TURN_SETTINGS_KEY] = str(turn)


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
        return utg_words.WordForm(utg_words.Word(type=utg_relations.WORD_TYPE.TEXT, forms=(self.date.verbose_full(),)))

    def linguistics_restrictions(self, now=None):
        restrictions = []

        for real_feast in tt_calendar.actual_real_feasts(now=now):
            restrictions.append(linguistics_restrictions.get(real_feast))

        for calendar_date in tt_calendar.actual_dates(self.date, tt_calendar.DATE):
            restrictions.append(linguistics_restrictions.get(calendar_date))

        for physics_date in tt_calendar.actual_dates(self.date, tt_calendar.PHYSICS_DATE):
            restrictions.append(linguistics_restrictions.get(physics_date))

        restrictions.append(linguistics_restrictions.get_raw('MONTH', self.date.month))
        restrictions.append(linguistics_restrictions.get_raw('QUINT', self.date.quint))
        restrictions.append(linguistics_restrictions.get_raw('QUINT_DAY', self.date.quint_day))

        restrictions.append(linguistics_restrictions.get(tt_calendar.day_type(self.date)))

        return restrictions


class LinguisticsTime(object):
    __slots__ = ('time', )

    def __init__(self, time):
        self.time = time

    @property
    def utg_name_form(self):
        return utg_words.WordForm(utg_words.Word(type=utg_relations.WORD_TYPE.TEXT, forms=(self.time.verbose(),)))

    def linguistics_restrictions(self, now=None):
        restrictions = []

        for day_time in tt_calendar.day_times(self.time):
            restrictions.append(linguistics_restrictions.get(day_time))

        return restrictions


def linguistics_date(turn=None):
    return LinguisticsDate(game_datetime(turn).date)


def linguistics_time(turn=None):
    return LinguisticsTime(game_datetime(turn).time)
