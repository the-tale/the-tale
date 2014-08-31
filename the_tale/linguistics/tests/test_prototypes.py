# coding: utf-8

import random

import mock

from utg import relations as utg_relations
from utg import words as utg_words
from utg import templates as utg_templates
from utg import dictionary as utg_dictionary

from the_tale.common.utils.testcase import TestCase

from the_tale.linguistics import prototypes
from the_tale.linguistics import relations
from the_tale.linguistics import storage
from the_tale.linguistics.lexicon import keys


class WordPrototypeTests(TestCase):

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


    def test_has_on_review_copy__on_review(self):
        prototype_1 = prototypes.WordPrototype.create(self.word_1)

        self.assertTrue(prototype_1.state.is_ON_REVIEW)
        self.assertFalse(prototype_1.has_on_review_copy())

        prototype_1.state = relations.WORD_STATE.IN_GAME
        prototype_1.save()

        prototype_2 = prototypes.WordPrototype.create(self.word_1)

        self.assertTrue(prototype_2.state.is_ON_REVIEW)
        self.assertFalse(prototype_2.has_on_review_copy())

    def test_has_on_review_copy__no_copy(self):
        prototype_1 = prototypes.WordPrototype.create(self.word_1)
        prototype_1.state = relations.WORD_STATE.IN_GAME
        prototype_1.save()

        self.assertTrue(prototype_1.state.is_IN_GAME)
        self.assertFalse(prototype_1.has_on_review_copy())

    def test_has_on_review_copy__has_copy(self):
        prototype_1 = prototypes.WordPrototype.create(self.word_1)
        prototype_1.state = relations.WORD_STATE.IN_GAME
        prototype_1.save()

        prototypes.WordPrototype.create(self.word_1)

        self.assertTrue(prototype_1.has_on_review_copy())


    def test_has_on_review_copy__no_copy__different_type(self):
        prototype_1 = prototypes.WordPrototype.create(self.word_1)
        prototype_1.state = relations.WORD_STATE.IN_GAME
        prototype_1.save()

        prototype_2 = prototypes.WordPrototype.create(self.word_1)
        prototype_2._model.type = self.word_type_2
        prototype_2.save()

        self.assertFalse(prototype_1.has_on_review_copy())


    def test_has_on_review_copy__no_copy__different_normal_form(self):
        prototype_1 = prototypes.WordPrototype.create(self.word_1)
        prototype_1.state = relations.WORD_STATE.IN_GAME
        prototype_1._model.save()

        prototype_2 = prototypes.WordPrototype.create(self.word_1)
        prototype_2._model.normal_form = u'new-normal-form'
        prototype_2._model.save()

        self.assertFalse(prototype_1.has_on_review_copy())




class TemplatePrototypeTests(TestCase):


    def create_template(self, key, word):
        text = u'[%(external)s|загл] 1 [%(word)s|%(external)s|буд,вн]' % {'external': key.variables[0].value, 'word': word}

        template = utg_templates.Template()

        template.parse(text, externals=[v.value for v in key.variables])

        return text, template


    def setUp(self):
        super(TemplatePrototypeTests, self).setUp()
        self.key_1, self.key_2 = random.sample(keys.LEXICON_KEY.records, 2)
        self.word_1 = u'пепельница'
        self.text_1, self.template_1 = self.create_template(self.key_1, word=self.word_1)

    def test_create(self):

        with self.check_delta(prototypes.TemplatePrototype._db_count, 1):
            prototype = prototypes.TemplatePrototype.create(key=self.key_1, raw_template=self.text_1, utg_template=self.template_1, verificators=[])

        self.assertTrue(prototype.state.is_ON_REVIEW)
        self.assertEqual(self.template_1, prototype.utg_template)
        self.assertEqual(self.text_1, prototype.raw_template)


    def test_save(self):
        prototype = prototypes.TemplatePrototype.create(key=self.key_1, raw_template=self.text_1, utg_template=self.template_1, verificators=[])
        prototype.utg_template.template = u'xxx'

        with self.check_not_changed(prototypes.TemplatePrototype._db_count):
            prototype.save()

        prototype.reload()
        self.assertEqual(prototype.utg_template.template, u'xxx')


    def test_get_errors__no_errors(self):
        key = keys.LEXICON_KEY.HERO_COMMON_JOURNAL_LEVEL_UP

        TEXT = u'[hero|загл] 1 [пепельница|hero|вн]'

        template = utg_templates.Template()

        template.parse(TEXT, externals=['hero'])

        verificator_1 = prototypes.Verificator(text=u'Призрак 1 w-1-ед,вн', externals={'hero': u'призрак', 'level': 13})
        verificator_2 = prototypes.Verificator(text=u'Привидение 1 w-1-ед,вн', externals={'hero': u'привидение', 'level': 13})
        verificator_3 = prototypes.Verificator(text=u'Русалка 1 w-1-ед,вн', externals={'hero': u'русалка', 'level': 13})

        dictionary = utg_dictionary.Dictionary()

        word = utg_words.Word.create_test_word(type=utg_relations.WORD_TYPE.NOUN, prefix=u'w-1-', only_required=True)
        word.forms[0] = u'пепельница'

        dictionary.add_word(word)
        dictionary.add_word(utg_words.Word(type=utg_relations.WORD_TYPE.NOUN, forms=[u'призрак'], properties=utg_words.Properties()))
        dictionary.add_word(utg_words.Word(type=utg_relations.WORD_TYPE.NOUN, forms=[u'привидение'], properties=utg_words.Properties()))
        dictionary.add_word(utg_words.Word(type=utg_relations.WORD_TYPE.NOUN, forms=[u'русалка'], properties=utg_words.Properties()))

        prototype = prototypes.TemplatePrototype.create(key=key,
                                                        raw_template=TEXT,
                                                        utg_template=template,
                                                        verificators=[verificator_1, verificator_2, verificator_3])

        errors = prototype.get_errors(utg_dictionary=dictionary)

        self.assertEqual(errors, [])


    def test_get_errors__word_errors(self):
        key = keys.LEXICON_KEY.HERO_COMMON_JOURNAL_LEVEL_UP

        TEXT = u'[hero|загл] 1 [пепельница|hero|вн]'

        template = utg_templates.Template()

        template.parse(TEXT, externals=['hero'])

        # verificators with error that would not be returned becouse of words_errors
        verificator_1 = prototypes.Verificator(text=u'', externals={'hero': u'призрак', 'level': 13})
        verificator_2 = prototypes.Verificator(text=u'Привидение 1 w-1-ед,вн', externals={'hero': u'привидение', 'level': 13})
        verificator_3 = prototypes.Verificator(text=u'Русалка 1 w-1-ед,дт', externals={'hero': u'русалка', 'level': 13})

        dictionary = utg_dictionary.Dictionary()

        dictionary.add_word(utg_words.Word(type=utg_relations.WORD_TYPE.NOUN, forms=[u'призрак'], properties=utg_words.Properties()))
        dictionary.add_word(utg_words.Word(type=utg_relations.WORD_TYPE.NOUN, forms=[u'привидение'], properties=utg_words.Properties()))
        dictionary.add_word(utg_words.Word(type=utg_relations.WORD_TYPE.NOUN, forms=[u'русалка'], properties=utg_words.Properties()))

        prototype = prototypes.TemplatePrototype.create(key=key,
                                                        raw_template=TEXT,
                                                        utg_template=template,
                                                        verificators=[verificator_1, verificator_2, verificator_3])

        errors = prototype.get_errors(utg_dictionary=dictionary)

        self.assertEqual(errors, [u'Неизвестное слово: «пепельница»'])


    def test_get_errors__verificators_errors(self):
        key = keys.LEXICON_KEY.HERO_COMMON_JOURNAL_LEVEL_UP

        TEXT = u'[hero|загл] 1 [пепельница|hero|вн]'

        template = utg_templates.Template()

        template.parse(TEXT, externals=['hero'])

        verificator_1 = prototypes.Verificator(text=u'', externals={'hero': u'призрак', 'level': 13})
        verificator_2 = prototypes.Verificator(text=u'Привидение 1 w-1-ед,вн', externals={'hero': u'привидение', 'level': 13})
        verificator_3 = prototypes.Verificator(text=u'Русалка 1 w-1-ед,дт', externals={'hero': u'русалка', 'level': 13})

        dictionary = utg_dictionary.Dictionary()

        word = utg_words.Word.create_test_word(type=utg_relations.WORD_TYPE.NOUN, prefix=u'w-1-', only_required=True)
        word.forms[0] = u'пепельница'

        dictionary.add_word(word)
        dictionary.add_word(utg_words.Word(type=utg_relations.WORD_TYPE.NOUN, forms=[u'призрак'], properties=utg_words.Properties()))
        dictionary.add_word(utg_words.Word(type=utg_relations.WORD_TYPE.NOUN, forms=[u'привидение'], properties=utg_words.Properties()))
        dictionary.add_word(utg_words.Word(type=utg_relations.WORD_TYPE.NOUN, forms=[u'русалка'], properties=utg_words.Properties()))

        prototype = prototypes.TemplatePrototype.create(key=key,
                                                        utg_template=template,
                                                        raw_template=TEXT,
                                                        verificators=[verificator_1, verificator_2, verificator_3])

        errors = prototype.get_errors(utg_dictionary=dictionary)

        self.assertEqual(errors, [u'Проверочный текст не совпадает с интерпретацией шаблона [Призрак 1 w-1-ед,вн]',
                                  u'Проверочный текст не совпадает с интерпретацией шаблона [Русалка 1 w-1-ед,вн]'])




class VerificatorTests(TestCase):

    def setUp(self):
        super(VerificatorTests, self).setUp()
        self.key = keys.LEXICON_KEY.HERO_COMMON_DIARY_CREATE

    def test_get_verificators__without_old(self):
        verificators = prototypes.Verificator.get_verificators(key=self.key)

        self.assertEqual(len(verificators), 3)

        self.assertEqual(verificators[0], prototypes.Verificator(text=u'', externals={'hero': u'призрак', 'level': 13}))
        self.assertEqual(verificators[1], prototypes.Verificator(text=u'', externals={'hero': u'привидение', 'level': 13}))
        self.assertEqual(verificators[2], prototypes.Verificator(text=u'', externals={'hero': u'русалка', 'level': 13}))


    def test_get_verificators__with_old(self):
        old_verificators = [prototypes.Verificator(text=u'1', externals={'hero': u'призрак'}),
                            prototypes.Verificator(text=u'2', externals={'hero': u'привидение', 'level': 13}),
                            prototypes.Verificator(text=u'3', externals={'hero': u'русалка', 'level': 13, 'xxx': 'yyy'})]

        verificators = prototypes.Verificator.get_verificators(key=self.key, old_verificators=old_verificators)

        self.assertEqual(len(verificators), 3)

        self.assertEqual(verificators[0], prototypes.Verificator(text=u'', externals={'hero': u'призрак', 'level': 13}))
        self.assertEqual(verificators[1], prototypes.Verificator(text=u'', externals={'hero': u'русалка', 'level': 13}))
        self.assertEqual(verificators[2], prototypes.Verificator(text=u'2', externals={'hero': u'привидение', 'level': 13}))
