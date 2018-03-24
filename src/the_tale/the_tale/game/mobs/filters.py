

def restrict_level(mobs, level):
    for mob, priority in mobs:
        if level < mob.level:
            continue
        yield (mob, priority)


def restrict_terrain(mobs, terrain):
    for mob, priority in mobs:
        if terrain not in mob.terrains:
            continue
        yield (mob, priority)


def restrict_mercenary(mobs, mercenary):
    for mob, priority in mobs:
        if mercenary != mob.is_mercenary:
            continue
        yield (mob, priority)


def change_type_priority(mobs, types, delta):
    for mob, priority in mobs:
        if mob.type in types:
            yield (mob, priority + delta)
            continue
        yield (mob, priority)
