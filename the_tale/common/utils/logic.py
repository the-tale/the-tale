# coding: utf-8
import random

def random_value_by_priority(values):

    if not values:
        return None

    domain = 0

    for value, priority in values:
        domain += priority

    choice_value = random.uniform(0, domain)

    for value, priority in values:
        if choice_value <= priority:
            return value
        choice_value -= priority

    raise Exception('unknown error in random_value_by_priority')


def pluralize_word(real_number, word_1, word_2_4, word_other):
        number = real_number % 100

        if number % 10 == 1 and number != 11:
            return '%d %s' % (real_number, word_1)
        elif 2 <= number % 10 <= 4 and not (12 <= number <= 14):
            return '%d %s' % (real_number, word_2_4)
        else:
            return '%d %s' % (real_number, word_other)

def verbose_timedelta(value):

    if value.days > 0:
        return pluralize_word(value.days, u'день', u'дня', u'дней')

    if value.seconds >= 60*60:
        return pluralize_word(value.seconds / (60*60) , u'час', u'часа', u'часов')

    if value.seconds >= 60:
        return pluralize_word(value.seconds / 60 , u'минута', u'минуты', u'минут')

    return u'меньше минуты'
