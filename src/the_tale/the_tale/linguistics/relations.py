# coding: utf-8

from rels import Column
from rels.django import DjangoEnum

from utg import relations as utg_relations

from the_tale.game import relations as game_relations
from the_tale.game.actions import relations as actions_relations
from the_tale.game.artifacts import relations as artifacts_relations
from the_tale.game.persons import relations as persons_relations
from the_tale.game.places import relations as places_relations
from the_tale.game.places import modifiers as places_modifiers
from the_tale.game.map import relations as map_relations
from the_tale.game.companions import relations as companions_relations
from the_tale.game.companions.abilities import effects as companion_effects


def word_type_record(name):
    utg_type = getattr(utg_relations.WORD_TYPE, name)
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
    records = ( ('ON_REVIEW', 0, 'на рассмотрении'),
                ('IN_GAME', 1, 'в игре'))


class WORD_USED_IN_STATUS(DjangoEnum):
    records = ( ('IN_INGAME_TEMPLATES', 0, 'во фразах игры'),
                ('IN_ONREVIEW_TEMPLATES', 1, 'только во фразах на рассмотрении'),
                ('NOT_USED', 2, 'не используется'))


class WORD_BLOCK_BASE(DjangoEnum):
    schema = Column(no_index=False)

    records = ( ('NC', 0, 'число-падеж', (utg_relations.NUMBER, utg_relations.CASE)),
                ('NCG', 1, 'число-падеж-род', (utg_relations.NUMBER, utg_relations.CASE, utg_relations.GENDER)),
                ('NP', 2, 'число-лицо', (utg_relations.NUMBER, utg_relations.PERSON)),
                ('NPG', 3, 'число-лицо-род', (utg_relations.NUMBER, utg_relations.PERSON, utg_relations.GENDER)),
                ('SINGLE', 4, 'одна форма', ()),
                ('NG', 5, 'число-род', (utg_relations.NUMBER, utg_relations.GENDER)),
                ('C', 6, 'падеж', (utg_relations.CASE, )),
                ('N', 7, 'число', (utg_relations.NUMBER, ))  )



class TEMPLATE_STATE(DjangoEnum):
    records = ( ('ON_REVIEW', 0, 'на рассмотрении'),
                ('IN_GAME', 1, 'в игре'),
                ('REMOVED', 2, 'удалена'))

class TEMPLATE_ERRORS_STATUS(DjangoEnum):
    records = ( ('NO_ERRORS', 0, 'нет ошибок'),
                ('HAS_ERRORS', 1, 'есть ошибки'))


class CONTRIBUTION_STATE(DjangoEnum):
    related_template_state = Column(related_name='contribution_state')
    related_word_state = Column(related_name='contribution_state')

    records = ( ('ON_REVIEW', 0, 'на рассмотрении', TEMPLATE_STATE.ON_REVIEW, WORD_STATE.ON_REVIEW),
                ('IN_GAME', 1, 'в игре', TEMPLATE_STATE.IN_GAME, WORD_STATE.IN_GAME))

class CONTRIBUTION_TYPE(DjangoEnum):
    records = ( ('WORD', 0, 'слово'),
                ('TEMPLATE', 1, 'фраза'))

class CONTRIBUTION_SOURCE(DjangoEnum):
    records = ( ('PLAYER', 0, 'игрок'),
                ('MODERATOR', 1, 'модератор'))


class INDEX_ORDER_BY(DjangoEnum):
    records = ( ('TEXT', 0, 'по тексту'),
                ('UPDATED_AT', 1, 'по дате') )


class WORD_HAS_PLURAL_FORM(DjangoEnum):
    records = ( ('HAS', 0, 'имеет'),
                ('HAS_NO', 1, 'не имеет'))


class TEMPLATE_RESTRICTION_GROUP(DjangoEnum):
    static_relation = Column(unique=False, single_type=False)

    records = ( ('GENDER', 0, 'пол', game_relations.GENDER),
                ('RACE', 1, 'раса', game_relations.RACE),
                ('CITY_MODIFIER', 2, 'специализация города', places_modifiers.CITY_MODIFIERS),
                ('HABIT_HONOR', 3, 'честь', game_relations.HABIT_HONOR_INTERVAL),
                ('HABIT_PEACEFULNESS', 4, 'миролюбие', game_relations.HABIT_PEACEFULNESS_INTERVAL),
                ('PERSON_TYPE', 5, 'профессия', persons_relations.PERSON_TYPE),

                ('ARTIFACT_TYPE', 6, 'тип экипировки', artifacts_relations.ARTIFACT_TYPE),
                ('ARTIFACT_POWER_TYPE', 7, 'тип силы', artifacts_relations.ARTIFACT_POWER_TYPE),
                ('ARTIFACT_RARITY', 8, 'редкость артефакта', artifacts_relations.RARITY),
                ('ARTIFACT_EFFECT', 9, 'эффект артефакта', artifacts_relations.ARTIFACT_EFFECT),

                ('MOB_TYPE', 10, 'тип существа', game_relations.BEING_TYPE),

                ('ARTIFACT', 11, 'артефакт', None),
                ('MOB', 12, 'монстр', None),
                ('COMPANION', 13, 'спутник', None),

                # ('COMPANION_TYPE', 14, u'тип спутника', companions_relations.TYPE),
                ('COMPANION_DEDICATION', 15, 'тип самоотверженности спутника', companions_relations.DEDICATION),
                # ('COMPANION_RARITY', 16, u'редкость спутника', companions_relations.RARITY),

                ('ARCHETYPE', 17, 'архетип', game_relations.ARCHETYPE),
                ('TERRAIN', 18, 'тип местности', map_relations.TERRAIN),
                ('BUILDING_TYPE', 19, 'тип здания', places_relations.BUILDING_TYPE),

                ('ACTION_TYPE', 20, 'тип действия героя', actions_relations.ACTION_TYPE),

                ('META_TERRAIN', 21, 'мета тип местности', map_relations.META_TERRAIN),
                ('META_HEIGHT', 22, 'мета тип высоты', map_relations.META_HEIGHT),
                ('META_VEGETATION', 23, 'мета тип растительности', map_relations.META_VEGETATION),

                ('COMMUNICATION_VERBAL', 24, 'вербальная коммуникация', game_relations.COMMUNICATION_VERBAL),
                ('COMMUNICATION_GESTURES', 25, 'невербальная коммуникация', game_relations.COMMUNICATION_GESTURES),
                ('COMMUNICATION_TELEPATHIC', 26, 'телепатия', game_relations.COMMUNICATION_TELEPATHIC),

                ('INTELLECT_LEVEL', 27, 'уровень интеллекта', game_relations.INTELLECT_LEVEL),

                ('ACTOR', 28, 'мета-тип существа', game_relations.ACTOR),

                ('PLURAL_FORM', 29, 'есть множественное число', WORD_HAS_PLURAL_FORM),

                ('PERSON_PERSONALITY_COSMETIC', 30, 'косметическая особенность характера', persons_relations.PERSONALITY_COSMETIC),
                ('PERSON_PERSONALITY_PRACTICAL', 31, 'практическая особенность характера', persons_relations.PERSONALITY_PRACTICAL),

                ('COMPANION_ABILITY', 32, 'особенность', companion_effects.ABILITIES),

                ('COMPANION_EXISTENCE', 33, 'наличие спутника', companions_relations.COMPANION_EXISTENCE),

                ('REAL_FEAST', 34, 'праздники из реального мира', game_relations.REAL_FEAST)
              )
