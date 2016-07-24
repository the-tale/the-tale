# coding: utf-8

from the_tale.game.balance import constants as c


def job_power(power, powers):
    # делим интервал от минимального до максимального размера проекта на равные куски
    # количество кусков равно количеству сущностей + 2
    # дополнительные сущности соответствуют фейковым худшей и лучшей
    # тогда даже если сущность одна, сила её проекта будет между минимумом и максимумом, но не будте равна им
    index = len([p for p in powers if p < power])

    interval = c.JOB_MAX_POWER - c.JOB_MIN_POWER
    delta = interval / (len(powers) + 1)

    return c.JOB_MIN_POWER + delta * (index + 1)
