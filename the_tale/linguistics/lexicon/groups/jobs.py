# coding: utf-8

from the_tale.linguistics.lexicon.relations import VARIABLE as V
from the_tale.linguistics.lexicon.groups.relations import LEXICON_GROUP

from the_tale.game.jobs import effects


DIARY_NAME_TEMPLATE = u'Дневник: работа выплнена {actor} {direction}, эффект: «{effect}», сообщение для {group}'
DIARY_DESCR_TEMPLATE = u'Работа выплнена {actor} {direction}, эффект: «{effect}», сообщение для {group}'

NAME_NAME_TEMPLATE = u'Название: выполняется {actor}, эффект: «{effect}»'
NAME_DESCR_TEMPLATE = u'Название занятия выполняемого {actor}, эффект: «{effect}»'


def name_record(actor, effect, index):
    name = u'job_name_{actor}_{effect}'.format(actor=actor, effect=effect.name).upper()

    arguments = {'actor': {'place': u'городом', 'person': u'мастером'}[actor],
                 'effect': effect.text}

    variables = [V.HERO, V.PLACE]
    if actor == 'person':
        variables.append(V.PERSON)

    return (name,
            LEXICON_GROUP.JOBS.index_group + index,
            NAME_NAME_TEMPLATE.format(**arguments),
            LEXICON_GROUP.JOBS,
            NAME_DESCR_TEMPLATE.format(**arguments),
            variables,
            None)


def diary_record(actor, effect, direction, group, index):
    name = u'job_diary_{actor}_{effect}_{direction}_{group}'.format(actor=actor,
                                                                    effect=effect.name,
                                                                    direction=direction,
                                                                    group=group).upper()

    arguments = {'actor': {'place': u'городом', 'person': u'мастером'}[actor],
                 'direction': {'positive': u'успешно', 'negative': u'не успешно'}[direction],
                 'effect': effect.text,
                 'group': {'friends': u'соратников', 'enemies': u'противников'}[group]}

    ui_template = None

    variables = [V.HERO, V.PLACE]
    if actor == 'person':
        variables.append(V.PERSON)

    has_rewards = ((direction, group) == ('positive', 'friends')) or ((direction, group) == ('negative', 'enemies'))

    if effect.is_HERO_MONEY and has_rewards:
        variables.append(V.COINS)
        ui_template = u'hero#N +coins#G'

    if effect.is_HERO_ARTIFACT and has_rewards:
        variables.append(V.ARTIFACT)

    if effect.is_HERO_EXPERIENCE and has_rewards:
        variables.append(V.EXPERIENCE)
        ui_template = u'hero#N +experience#EXP'

    if effect.is_HERO_ENERGY and has_rewards:
        variables.append(V.ENERGY)
        ui_template = u'hero#N +energy#EN'

    return (name,
            LEXICON_GROUP.JOBS.index_group + index,
            DIARY_NAME_TEMPLATE.format(**arguments),
            LEXICON_GROUP.JOBS,
            DIARY_DESCR_TEMPLATE.format(**arguments),
            variables,
            ui_template)


def create_keys():
    keys = []

    index = 0

    for actor in ('place', 'person'):
        for effect in effects.EFFECT.records:
            keys.append(name_record(actor, effect, index))
            index += 1

    for actor in ('place', 'person'):
        for effect in effects.EFFECT.records:
            for direction in ('positive', 'negative'):
                for group in ('friends', 'enemies'):
                    keys.append(diary_record(actor, effect, direction, group, index))
                    index += 1

    return keys

KEYS = create_keys()
