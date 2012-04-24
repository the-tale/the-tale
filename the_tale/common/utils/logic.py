# coding: utf-8
import random

def random_value_by_priority(values):
    domain = 0

    for value, priority in values:
        domain += priority

    choice_value = random.uniform(0, domain)

    for value, priority in values:
        if choice_value <= priority:
            return value
        choice_value -= priority

    raise Exception('unknown error in random_value_by_priority')
