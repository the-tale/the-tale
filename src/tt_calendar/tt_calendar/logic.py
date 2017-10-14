
import datetime

from . import relations


def actual_real_feasts(now=None):
    if now is None:
        now = datetime.datetime.utcnow()

    now = now.replace(year=datetime.MINYEAR)

    for feast in relations.REAL_FEAST.records:
        for interval in feast.intervals:
            if interval[0] <= now <= interval[1]:
                yield feast
                break


def actual_dates(now, relation):
    for date in relation.records:
        for interval in date.intervals:
            if interval[0] <= (now.month, now.day) <= interval[1]:
                yield date
                break


def is_day_off(date):
    if date.day in (14, 29, 44, 59, 74, 89):
        return True

    if date.month == relations.MONTH.DRY.value and date.day == 1:
        return True

    return False


def day_type(date):
    if is_day_off(date):
        return relations.DAY_TYPE.DAY_OFF

    return relations.DAY_TYPE.WEEKDAY


def day_times(time):
    if time.hour < 7 or 19 <= time.hour:
        yield relations.DAY_TIME.DARK_TIME
    else:
        yield relations.DAY_TIME.LIGHT_TIME

    if time.hour < 7:
        yield relations.DAY_TIME.NIGHT
    elif time.hour < 10:
        yield relations.DAY_TIME.MORNING
    elif time.hour < 16:
        yield relations.DAY_TIME.DAY
    elif time.hour < 19:
        yield relations.DAY_TIME.EVENING
    else:
        yield relations.DAY_TIME.NIGHT

    if time.hour == 7:
        yield relations.DAY_TIME.DAWN

    if time.hour == 19:
        yield relations.DAY_TIME.SUNSET
