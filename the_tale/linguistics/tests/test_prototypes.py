# coding: utf-8

import random

import mock

from utg import relations as utg_relations
from utg import words as utg_words
from utg import templates as utg_templates

from the_tale.common.utils import testcase

from the_tale.accounts.prototypes import AccountPrototype
from the_tale.accounts.logic import register_user

from the_tale.game.logic import create_test_map

from the_tale.linguistics import prototypes
from the_tale.linguistics import relations
from the_tale.linguistics import storage

from the_tale.linguistics.lexicon import keys
from the_tale.linguistics.lexicon import logic as lexicon_logic


class WordPrototypeTests(testcase.TestCase):

    def setUp(self):
        super(WordPrototypeTests, self).setUp()
        self.word_type_1, self.word_type_2 = random.sample(utg_relations.WORD_TYPE.records, 2)
        self.word_1 = utg_words.Word.create_test_word(self.word_type_1)

    def test_create(self):

        with mock.patch('the_tale.linguistics.storage.raw_dictionary.refresh') as raw_refresh:
            with mock.patch('the_tale.linguistics.storage.game_dictionary.refresh') as game_refresh:
                with self.check_changed(lambda: storage.raw_dictionary.version):
                    with self.check_not_changed(lambda: storage.game_dictionary.version):
                        with self.check_delta(prototypes.WordPrototype._db_count, 1):
                            prototype = prototypes.WordPrototype.create(self.word_1)

        self.assertEqual(raw_refresh.call_count, 1)
        self.assertEqual(game_refresh.call_count, 0)

        self.assertTrue(prototype.state.is_ON_REVIEW)
        self.assertEqual(self.word_1, prototype.utg_word)
        self.assertEqual(self.word_1.normal_form(), prototype.utg_word.normal_form())


    def test_save(self):
        prototype = prototypes.WordPrototype.create(self.word_1)
        prototype.utg_word.forms[0] = u'xxx'

        with mock.patch('the_tale.linguistics.storage.raw_dictionary.refresh') as raw_refresh:
            with mock.patch('the_tale.linguistics.storage.game_dictionary.refresh') as game_refresh:
                with self.check_changed(lambda: storage.raw_dictionary.version):
                    with self.check_not_changed(lambda: storage.game_dictionary.version):
                        with self.check_not_changed(prototypes.WordPrototype._db_count):
                            prototype.save()

        self.assertEqual(raw_refresh.call_count, 1)
        self.assertEqual(game_refresh.call_count, 0)

        prototype.reload()
        self.assertEqual(prototype.utg_word.forms[0], u'xxx')


    def test_save__in_game(self):
        prototype = prototypes.WordPrototype.create(self.word_1)
        prototype.utg_word.forms[0] = u'xxx'
        prototype.state = relations.WORD_STATE.IN_GAME

        with mock.patch('the_tale.linguistics.storage.raw_dictionary.refresh') as raw_refresh:
            with mock.patch('the_tale.linguistics.storage.game_dictionary.refresh') as game_refresh:
                with self.check_changed(lambda: storage.raw_dictionary.version):
                    with self.check_changed(lambda: storage.game_dictionary.version):
                        with self.check_not_changed(prototypes.WordPrototype._db_count):
                            prototype.save()

        self.assertEqual(raw_refresh.call_count, 1)
        self.assertEqual(game_refresh.call_count, 1)

        prototype.reload()
        self.assertEqual(prototype.utg_word.forms[0], u'xxx')



class TemplatePrototypeTests(testcase.TestCase):

    def create_template(self, key, word):
        text = u'[%(external)s|загл] 1 [%(word)s|%(external)s|буд,вн]' % {'external': key.variables[0].value, 'word': word}

        template = utg_templates.Template()

        template.parse(text, externals=[v.value for v in key.variables])

        return text, template


    def setUp(self):
        super(TemplatePrototypeTests, self).setUp()

        create_test_map()

        result, account_id, bundle_id = register_user('test_user1', 'test_user_1@test.com', '111111')
        self.account_1 = AccountPrototype.get_by_id(account_id)

        storage.raw_dictionary.refresh()
        storage.game_dictionary.refresh()

        self.key_1, self.key_2 = random.sample(keys.LEXICON_KEY.records, 2)
        self.word_1 = u'пепельница'
        self.text_1, self.template_1 = self.create_template(self.key_1, word=self.word_1)

    def test_create(self):

        with self.check_delta(prototypes.TemplatePrototype._db_count, 1):
            prototype = prototypes.TemplatePrototype.create(key=self.key_1, raw_template=self.text_1, utg_template=self.template_1, verificators=[], author=self.account_1)

        self.assertTrue(prototype.state.is_ON_REVIEW)
        self.assertEqual(self.template_1, prototype.utg_template)
        self.assertEqual(self.text_1, prototype.raw_template)


    def test_save(self):
        prototype = prototypes.TemplatePrototype.create(key=self.key_1, raw_template=self.text_1, utg_template=self.template_1, verificators=[], author=self.account_1)
        prototype.utg_template.template = u'xxx'

        with self.check_not_changed(prototypes.TemplatePrototype._db_count):
            prototype.save()

        prototype.reload()
        self.assertEqual(prototype.utg_template.template, u'xxx')


    def test_get_errors__no_errors(self):
        key = keys.LEXICON_KEY.HERO_COMMON_JOURNAL_LEVEL_UP

        TEXT = u'[hero|загл] [level] [неизвестное слово|hero|вн]'

        template = utg_templates.Template()

        template.parse(TEXT, externals=['hero'])

        verificator_1 = prototypes.Verificator(text=u'Героиня 1 w-1-ед,вн,жр,од,пол', externals={'hero': (u'героиня', u''), 'level': (1, u'')})
        verificator_2 = prototypes.Verificator(text=u'Рыцари 5 w-1-мн,вн,од,пол', externals={'hero': (u'рыцарь', u'мн'), 'level': (5, u'')})
        verificator_3 = prototypes.Verificator(text=u'Герой 2 w-1-ед,вн,мр,од,пол', externals={'hero': (u'герой', u''), 'level': (2, u'')})
        verificator_4 = prototypes.Verificator(text=u'Привидение 5 w-1-ед,вн,ср,од,пол', externals={'hero': (u'привидение', u''), 'level': (5, u'')})

        dictionary = storage.raw_dictionary.item

        word = utg_words.Word.create_test_word(type=utg_relations.WORD_TYPE.ADJECTIVE, prefix=u'w-1-', only_required=True)
        word.forms[0] = u'неизвестное слово'

        dictionary.add_word(word)

        prototype = prototypes.TemplatePrototype.create(key=key,
                                                        raw_template=TEXT,
                                                        utg_template=template,
                                                        verificators=[verificator_1, verificator_2, verificator_3, verificator_4],
                                                        author=self.account_1)

        errors = prototype.get_errors(utg_dictionary=dictionary)

        self.assertEqual(errors, [])


    def test_get_errors__word_errors(self):
        key = keys.LEXICON_KEY.HERO_COMMON_JOURNAL_LEVEL_UP

        TEXT = u'[hero|загл] [level] [неизвестное слово|hero|вн]'

        template = utg_templates.Template()

        template.parse(TEXT, externals=['hero'])

        # verificators with error that would not be returned becouse of words_errors
        verificator_1 = prototypes.Verificator(text=u'абракадабра', externals={'hero': (u'героиня', u''), 'level': (1, u'')})
        verificator_2 = prototypes.Verificator(text=u'Рыцарь 5 w-1-ед,вн', externals={'hero': (u'рыцарь', u'мн'), 'level': (5, u'')})
        verificator_3 = prototypes.Verificator(text=u'Герой 2 w-1-ед,вн', externals={'hero': (u'герой', u''), 'level': (2, u'')})
        verificator_4 = prototypes.Verificator(text=u'', externals={'hero': (u'привидение', u''), 'level': (5, u'')})

        prototype = prototypes.TemplatePrototype.create(key=key,
                                                        raw_template=TEXT,
                                                        utg_template=template,
                                                        verificators=[verificator_1, verificator_2, verificator_3, verificator_4],
                                                        author=self.account_1)

        errors = prototype.get_errors(utg_dictionary=storage.raw_dictionary.item)

        self.assertEqual(errors, [u'Неизвестное слово: «неизвестное слово»'])


    def test_get_errors__verificators_errors(self):
        key = keys.LEXICON_KEY.HERO_COMMON_JOURNAL_LEVEL_UP

        TEXT = u'[hero|загл] [level] [неизвестное слово|hero|вн]'

        template = utg_templates.Template()

        template.parse(TEXT, externals=['hero'])

        verificator_1 = prototypes.Verificator(text=u'абракадабра', externals={'hero': (u'героиня', u''), 'level': (1, u'')})
        verificator_2 = prototypes.Verificator(text=u'Рыцари 5 w-1-мн,вн,од,пол', externals={'hero': (u'рыцарь', u'мн'), 'level': (5, u'')})
        verificator_3 = prototypes.Verificator(text=u'Герой 2 w-1-ед,вн', externals={'hero': (u'герой', u''), 'level': (2, u'')})
        verificator_4 = prototypes.Verificator(text=u'', externals={'hero': (u'привидение', u''), 'level': (5, u'')})

        dictionary = storage.raw_dictionary.item

        word = utg_words.Word.create_test_word(type=utg_relations.WORD_TYPE.ADJECTIVE, prefix=u'w-1-', only_required=True)
        word.forms[0] = u'неизвестное слово'

        dictionary.add_word(word)

        prototype = prototypes.TemplatePrototype.create(key=key,
                                                        utg_template=template,
                                                        raw_template=TEXT,
                                                        verificators=[verificator_1, verificator_2, verificator_3, verificator_4],
                                                        author=self.account_1)

        errors = prototype.get_errors(utg_dictionary=dictionary)

        self.assertEqual(errors, [u'Проверочный текст не совпадает с интерпретацией шаблона [Героиня 1 w-1-ед,вн,жр,од,пол]',
                                  u'Проверочный текст не совпадает с интерпретацией шаблона [Герой 2 w-1-ед,вн,мр,од,пол]',
                                  u'Проверочный текст не совпадает с интерпретацией шаблона [Привидение 5 w-1-ед,вн,ср,од,пол]'])




class VerificatorTests(testcase.TestCase):

    def setUp(self):
        super(VerificatorTests, self).setUp()
        self.key = keys.LEXICON_KEY.HERO_COMMON_DIARY_CREATE

    def test_get_verificators__without_old(self):
        groups = lexicon_logic.get_verificators_groups(key=keys.LEXICON_KEY.HERO_COMMON_JOURNAL_LEVEL_UP, old_groups={})
        self.assertEqual(groups, {'hero': (0, 0), 'level': (1, 0)})

        verificators = prototypes.Verificator.get_verificators(key=self.key, groups=groups)

        self.assertEqual(len(verificators), 4)

        self.assertEqual(verificators[0], prototypes.Verificator(text=u'', externals={'hero': (u'героиня', u''), 'level': (1, u'')}))
        self.assertEqual(verificators[1], prototypes.Verificator(text=u'', externals={'hero': (u'рыцарь', u'мн'), 'level': (5, u'')}))
        self.assertEqual(verificators[2], prototypes.Verificator(text=u'', externals={'hero': (u'герой', u''), 'level': (2, u'')}))
        self.assertEqual(verificators[3], prototypes.Verificator(text=u'', externals={'hero': (u'привидение', u''), 'level': (5, u'')}))


    def test_get_verificators__with_old(self):
        groups = lexicon_logic.get_verificators_groups(key=keys.LEXICON_KEY.HERO_COMMON_JOURNAL_LEVEL_UP, old_groups={})
        self.assertEqual(groups, {'hero': (0, 0), 'level': (1, 0)})

        old_verificators = [prototypes.Verificator(text=u'1', externals={'hero': (u'привидение', u''), 'level': (1, u'')}),
                            prototypes.Verificator(text=u'2', externals={'hero': (u'героиня', u''), 'level': (1, u'')}),
                            prototypes.Verificator(text=u'3', externals={'hero': (u'рыцарь', u'ед'), 'level': (5, u'')}),
                            prototypes.Verificator(text=u'4', externals={'hero': (u'абракадабра', u''), 'level': (5, u'')}),
                            prototypes.Verificator(text=u'5', externals={'hero': (u'герой', u''), 'level': (2, u'')}) ]

        verificators = prototypes.Verificator.get_verificators(key=self.key, groups=groups, old_verificators=old_verificators)

        self.assertEqual(len(verificators), 4)

        self.assertEqual(verificators[0], prototypes.Verificator(text=u'1', externals={'hero': (u'привидение', u''), 'level': (1, u'')}))
        self.assertEqual(verificators[1], prototypes.Verificator(text=u'5', externals={'hero': (u'герой', u''), 'level': (2, u'')}))
        self.assertEqual(verificators[2], prototypes.Verificator(text=u'', externals={'hero': (u'рыцарь', u'мн'), 'level': (5, u'')}))
        self.assertEqual(verificators[3], prototypes.Verificator(text=u'', externals={'hero': (u'героиня', u''), 'level': (5, u'')}))
