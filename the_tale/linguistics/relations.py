# coding: utf-8

from rels import Column
from rels.django import DjangoEnum

from utg import relations as utg_relations

from the_tale.game import relations as game_relations
from the_tale.game.artifacts import relations as artifacts_relations
from the_tale.game.mobs import relations as mobs_relations
from the_tale.game.persons import relations as persons_relations
from the_tale.game.map.places import relations as places_relations
from the_tale.game.map import relations as map_relations
from the_tale.game.companions import relations as companions_relations


def word_type_record(name):
    utg_type = utg_relations.WORD_TYPE.index_name[name]
    return (name,
            utg_type.value,
            utg_type.text,
            utg_type)

class ALLOWED_WORD_TYPE(DjangoEnum):
    utg_type = Column()

    records = ( word_type_record('NOUN'),
                word_type_record('ADJECTIVE'),
                word_type_record('PRONOUN'),
                word_type_record('VERB'),
                word_type_record('PARTICIPLE'),
                word_type_record('PREPOSITION') )


class WORD_STATE(DjangoEnum):
    records = ( ('ON_REVIEW', 0, u'на рассмотрении'),
                ('IN_GAME', 1, u'в игре'))


class WORD_USED_IN_STATUS(DjangoEnum):
    records = ( ('IN_INGAME_TEMPLATES', 0, u'во фразах игры'),
                ('IN_ONREVIEW_TEMPLATES', 1, u'только во фразах на рассмотрении'),
                ('NOT_USED', 2, u'не используется'))


class WORD_BLOCK_BASE(DjangoEnum):
    schema = Column()

    records = ( ('NC', 0, u'число-падеж', (utg_relations.NUMBER, utg_relations.CASE)),
                ('NCG', 1, u'число-падеж-род', (utg_relations.NUMBER, utg_relations.CASE, utg_relations.GENDER)),
                ('NP', 2, u'число-лицо', (utg_relations.NUMBER, utg_relations.PERSON)),
                ('NPG', 3, u'число-лицо-род', (utg_relations.NUMBER, utg_relations.PERSON, utg_relations.GENDER)),
                ('SINGLE', 4, u'одна форма', ()),
                ('NG', 5, u'число-род', (utg_relations.NUMBER, utg_relations.GENDER)),
                ('C', 6, u'падеж', (utg_relations.CASE, )),
                ('N', 7, u'число', (utg_relations.NUMBER, ))  )



class TEMPLATE_STATE(DjangoEnum):
    records = ( ('ON_REVIEW', 0, u'на рассмотрении'),
                ('IN_GAME', 1, u'в игре'))

class TEMPLATE_ERRORS_STATUS(DjangoEnum):
    records = ( ('NO_ERRORS', 0, u'нет ошибок'),
                ('HAS_ERRORS', 1, u'есть ошибки'))


class CONTRIBUTION_TYPE(DjangoEnum):
    records = ( ('WORD', 0, u'слово'),
                ('TEMPLATE', 1, u'фраза'))


class INDEX_ORDER_BY(DjangoEnum):
    records = ( ('TEXT', 0, u'по тексту'),
                ('UPDATED_AT', 1, u'по дате') )


class TEMPLATE_RESTRICTION_GROUP(DjangoEnum):
    static_relation = Column(unique=False, single_type=False)

    records = ( ('GENDER', 0, u'пол', game_relations.GENDER),
                ('RACE', 1, u'раса', game_relations.RACE),
                ('CITY_MODIFIER', 2, u'специализация города', places_relations.CITY_MODIFIERS),
                ('HABIT_HONOR', 3, u'честь', game_relations.HABIT_HONOR_INTERVAL),
                ('HABIT_PEACEFULNESS', 4, u'миролюбие', game_relations.HABIT_PEACEFULNESS_INTERVAL),
                ('PERSON_TYPE', 5, u'профессия', persons_relations.PERSON_TYPE),

                ('ARTIFACT_TYPE', 6, u'тип экипировки', artifacts_relations.ARTIFACT_TYPE),
                ('ARTIFACT_POWER_TYPE', 7, u'тип силы', artifacts_relations.ARTIFACT_POWER_TYPE),
                ('ARTIFACT_RARITY', 8, u'редкость артефакта', artifacts_relations.RARITY),
                ('ARTIFACT_EFFECT', 9, u'эффект артефакта', artifacts_relations.ARTIFACT_EFFECT),

                ('MOB_TYPE', 10, u'тип монстра', mobs_relations.MOB_TYPE),

                ('ARTIFACT', 11, u'артефакт', None),
                ('MOB', 12, u'монстр', None),
                ('COMPANION', 13, u'спутник', None),

                ('COMPANION_TYPE', 14, u'тип спутника', companions_relations.TYPE),
                ('COMPANION_DEDICATION', 15, u'тип самоотверженности спутника', companions_relations.DEDICATION),
                ('COMPANION_RARITY', 16, u'редкость спутника', companions_relations.RARITY),

                ('ARCHETYPE', 17, u'архетип спутника', game_relations.ARCHETYPE),
                ('TERRAIN', 18, u'тип местности', map_relations.TERRAIN),
                ('BUILDING_TYPE', 19, u'тип здания', places_relations.BUILDING_TYPE),
                 )
