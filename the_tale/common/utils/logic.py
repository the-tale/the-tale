# coding: utf-8
import math
import random
import subprocess

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


def shuffle_values_by_priority(values):

    result = []

    working_values = list(values)

    while working_values:
        choosen_value = random_value_by_priority(working_values)
        working_values = [(value, priority) for value, priority in working_values if value != choosen_value]
        result.append(choosen_value)

    return result


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

    elif value.days == 0:
        if value.seconds >= 60*60:
            return pluralize_word(value.seconds / (60*60) , u'час', u'часа', u'часов')

        if value.seconds >= 60:
            return pluralize_word(value.seconds / 60 , u'минута', u'минуты', u'минут')

    return u'меньше минуты'


def choose_from_interval(value, intervals):

    choosen_result = None
    for test_value, result in reversed(intervals):
        if test_value <= value:
            choosen_result = result
            break

    return choosen_result

def choose_nearest(value, intervals):
    choosen_result = None
    min_delta = 999999
    for test_value, result in intervals:
        delta = math.fabs(test_value - value)
        if delta < min_delta:
            min_delta = delta
            choosen_result = result

    return choosen_result


def split_into_table(sequence, columns):
    table = []

    items_number = len(sequence)

    start_index = 0

    for i in xrange(columns):
        sublen = int(math.ceil(items_number / float(columns-i)))
        table.append(sequence[start_index:start_index+sublen])
        items_number -= sublen
        start_index += sublen

    for i in xrange(1, columns):
        while len(table[0]) > len(table[i]):
            table[i].append(None)

    table = zip(*table)

    return table



def get_or_create(get_method, create_method, exception, kwargs):

    obj = get_method(**kwargs)

    if obj is not None:
        return obj

    try:
        return create_method(**kwargs)
    except exception:
        return get_method(**kwargs)


def run_django_command(command):
    return subprocess.call(['django-admin.py']+command+['--settings', 'the_tale.settings'])
