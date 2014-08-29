# coding: utf-8

from the_tale.linguistics.lexicon.relations import VARIABLE as V


def key(name, id, text, description, variables):
    from the_tale.linguistics.lexicon.relations import LEXICON_GROUP
    group = LEXICON_GROUP.HERO_COMMON
    return ('%s_%s' % (group.name.upper(), name.upper()),
            group.index_group + id,
            text,
            group,
            description,
            variables)



KEYS = [key('journal_level_up', 0, u'Получение уровня', u'Герой получает уровень.', [V.HERO, V.LEVEL]),
        key('diary_create', 1, u'Создание героя', u'Первая запись героя в дневнике.', [V.HERO]),
        key('journal_create_1', 2, u'Создание героя, фраза 1', u'Фраза 1 в журнале героя — первая мысль о геройстве', [V.HERO]),
        key('journal_create_2', 3, u'Создание героя, фраза 2', u'Фраза 2 в журнале героя — мысль о будущем.', [V.HERO]),
        key('journal_create_3', 4, u'Создание героя, фраза 3', u'Фраза 3 в журнале героя — мысль о героях.', [V.HERO]),
        key('journal_create_4', 5, u'Создание героя, фраза 4', u'Фраза 4 в журнале героя — мысль о текущей ситуации.', [V.HERO])]
