
import smart_imports

smart_imports.all()


def word_type_record(name):
    utg_type = getattr(utg_relations.WORD_TYPE, name)
    return (name,
            utg_type.value,
            utg_type.text,
            utg_type)


class ALLOWED_WORD_TYPE(rels_django.DjangoEnum):
    utg_type = rels.Column()

    records = (word_type_record('NOUN'),
               word_type_record('ADJECTIVE'),
               word_type_record('PRONOUN'),
               word_type_record('VERB'),
               word_type_record('PARTICIPLE'),
               word_type_record('PREPOSITION'))


class WORD_STATE(rels_django.DjangoEnum):
    records = (('ON_REVIEW', 0, 'на рассмотрении'),
               ('IN_GAME', 1, 'в игре'))


class WORD_USED_IN_STATUS(rels_django.DjangoEnum):
    records = (('IN_INGAME_TEMPLATES', 0, 'во фразах игры'),
               ('IN_ONREVIEW_TEMPLATES', 1, 'только во фразах на рассмотрении'),
               ('NOT_USED', 2, 'не используется'))


class WORD_BLOCK_BASE(rels_django.DjangoEnum):
    schema = rels.Column(no_index=False)

    records = (('NC', 0, 'число-падеж', (utg_relations.NUMBER, utg_relations.CASE)),
               ('NCG', 1, 'число-падеж-род', (utg_relations.NUMBER, utg_relations.CASE, utg_relations.GENDER)),
               ('NP', 2, 'число-лицо', (utg_relations.NUMBER, utg_relations.PERSON)),
               ('NPG', 3, 'число-лицо-род', (utg_relations.NUMBER, utg_relations.PERSON, utg_relations.GENDER)),
               ('SINGLE', 4, 'одна форма', ()),
               ('NG', 5, 'число-род', (utg_relations.NUMBER, utg_relations.GENDER)),
               ('C', 6, 'падеж', (utg_relations.CASE, )),
               ('N', 7, 'число', (utg_relations.NUMBER, )))


class TEMPLATE_STATE(rels_django.DjangoEnum):
    records = (('ON_REVIEW', 0, 'на рассмотрении'),
               ('IN_GAME', 1, 'в игре'),
               ('REMOVED', 2, 'удалена'))


class TEMPLATE_ERRORS_STATUS(rels_django.DjangoEnum):
    records = (('NO_ERRORS', 0, 'нет ошибок'),
               ('HAS_ERRORS', 1, 'есть ошибки'))


class CONTRIBUTION_STATE(rels_django.DjangoEnum):
    related_template_state = rels.Column(related_name='contribution_state')
    related_word_state = rels.Column(related_name='contribution_state')

    records = (('ON_REVIEW', 0, 'на рассмотрении', TEMPLATE_STATE.ON_REVIEW, WORD_STATE.ON_REVIEW),
               ('IN_GAME', 1, 'в игре', TEMPLATE_STATE.IN_GAME, WORD_STATE.IN_GAME))


class CONTRIBUTION_TYPE(rels_django.DjangoEnum):
    records = (('WORD', 0, 'слово'),
               ('TEMPLATE', 1, 'фраза'))


class CONTRIBUTION_SOURCE(rels_django.DjangoEnum):
    records = (('PLAYER', 0, 'игрок'),
               ('MODERATOR', 1, 'модератор'))


class INDEX_ORDER_BY(rels_django.DjangoEnum):
    records = (('TEXT', 0, 'по тексту'),
               ('UPDATED_AT', 1, 'по дате'))


class WORD_HAS_PLURAL_FORM(rels_django.DjangoEnum):
    records = (('HAS', 0, 'имеет'),
               ('HAS_NO', 1, 'не имеет'))
