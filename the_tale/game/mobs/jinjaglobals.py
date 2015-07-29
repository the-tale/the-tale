# coding: utf-8

from dext.common.utils import jinja2


@jinja2.jinjaglobal
def mob_communication_abilities(mob):
    levels = []

    if mob.communication_verbal.is_CAN:
        levels.append(u'вербальная')

    if mob.communication_gestures.is_CAN:
        levels.append(u'невербальная')

    if mob.communication_telepathic.is_CAN:
        levels.append(u'телепатия')

    if not levels:
        levels.append(u'—')

    return u', '.join(levels)
