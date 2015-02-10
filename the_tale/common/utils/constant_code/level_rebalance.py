# coding: utf-8

OLD_EXP_PER_HOUR = 10
OLD_TIME_TO_LVL_DELTA = 5

NEW_EXP_PER_HOUR = 10
NEW_TIME_TO_LVL_DELTA = 7
NEW_TIME_TO_LVL_MULTIPLIER = 1.02



def old_level_to_exp(level, exp):
    total_exp = exp
    for i in range(2, level+1):
        total_exp += i * OLD_TIME_TO_LVL_DELTA * OLD_EXP_PER_HOUR
    return total_exp


def new_time_on_lvl(lvl):
    return float(NEW_TIME_TO_LVL_DELTA * lvl * NEW_TIME_TO_LVL_MULTIPLIER ** lvl)


def exp_to_new_level(exp):
    level = 1

    while exp >= new_time_on_lvl(level+1) * NEW_EXP_PER_HOUR:
        exp -= new_time_on_lvl(level+1) * NEW_EXP_PER_HOUR
        level += 1

    return level, exp


def old_to_new(level, exp):
    raw_exp = old_level_to_exp(level, exp)
    return exp_to_new_level(raw_exp)
