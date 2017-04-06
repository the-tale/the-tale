# coding: utf-8

import random

from unittest import mock

from utg import relations as utg_relations
from utg import words as utg_words
from utg import templates as utg_templates

from the_tale.common.utils import testcase

from the_tale.game.logic import create_test_map

from the_tale.linguistics import prototypes
from the_tale.linguistics import relations
from the_tale.linguistics import storage
from the_tale.linguistics import logic
from the_tale.linguistics import models

from the_tale.linguistics.lexicon import keys
from the_tale.linguistics.lexicon import logic as lexicon_logic


class WordPrototypeTests(testcase.TestCase):

    def setUp(self):
        super(WordPrototypeTests, self).setUp()
        self.word_type_1, self.word_type_2 = random.sample(utg_relations.WORD_TYPE.records, 2)
        self.word_1 = utg_words.Word.create_test_word(self.word_type_1)

    def test_create(self):

        with mock.patch('the_tale.linguistics.workers.linguistics_manager.Worker.cmd_game_dictionary_changed') as cmd_game_dictionary_changed:
            with mock.patch('the_tale.linguistics.storage.game_dictionary.refresh') as game_refresh:
                with self.check_not_changed(lambda: storage.game_dictionary.version):
                    with self.check_delta(prototypes.WordPrototype._db_count, 1):
                        prototype = prototypes.WordPrototype.create(self.word_1)

        self.assertEqual(game_refresh.call_count, 0)
        self.assertEqual(cmd_game_dictionary_changed.call_count, 1)

        self.assertTrue(prototype.state.is_ON_REVIEW)
        self.assertEqual(self.word_1, prototype.utg_word)
        self.assertEqual(self.word_1.normal_form(), prototype.utg_word.normal_form())


    def test_save(self):
        prototype = prototypes.WordPrototype.create(self.word_1)
        prototype.utg_word.forms[0] = 'xxx'


        with mock.patch('the_tale.linguistics.workers.linguistics_manager.Worker.cmd_game_dictionary_changed') as cmd_game_dictionary_changed:
            with mock.patch('the_tale.linguistics.storage.game_dictionary.refresh') as game_refresh:
                with self.check_not_changed(lambda: storage.game_dictionary.version):
                    with self.check_not_changed(prototypes.WordPrototype._db_count):
                        prototype.save()

        self.assertEqual(game_refresh.call_count, 0)
        self.assertEqual(cmd_game_dictionary_changed.call_count, 1)

        prototype.reload()
        self.assertEqual(prototype.utg_word.forms[0], 'xxx')


    def test_save__in_game(self):
        prototype = prototypes.WordPrototype.create(self.word_1)
        prototype.utg_word.forms[0] = 'xxx'
        prototype.state = relations.WORD_STATE.IN_GAME

        with mock.patch('the_tale.linguistics.storage.game_dictionary.refresh') as game_refresh:
            with self.check_changed(lambda: storage.game_dictionary.version):
                with self.check_not_changed(prototypes.WordPrototype._db_count):
                    prototype.save()

        self.assertEqual(game_refresh.call_count, 1)

        prototype.reload()
        self.assertEqual(prototype.utg_word.forms[0], 'xxx')

    def test_update_used_in_status__in_game(self):
        word = prototypes.WordPrototype.create(self.word_1)

        word.update_used_in_status(used_in_ingame_templates=1, used_in_onreview_templates=2)

        self.assertEqual(word.used_in_ingame_templates, 1)
        self.assertEqual(word.used_in_onreview_templates, 2)
        self.assertTrue(word.used_in_status.is_IN_INGAME_TEMPLATES)

    def test_update_used_in_status__on_review(self):
        word = prototypes.WordPrototype.create(self.word_1)

        word.update_used_in_status(used_in_ingame_templates=0, used_in_onreview_templates=2)

        self.assertEqual(word.used_in_ingame_templates, 0)
        self.assertEqual(word.used_in_onreview_templates, 2)
        self.assertTrue(word.used_in_status.is_IN_ONREVIEW_TEMPLATES)

    def test_update_used_in_status__not_used(self):
        word = prototypes.WordPrototype.create(self.word_1)

        word.update_used_in_status(used_in_ingame_templates=0, used_in_onreview_templates=0)

        self.assertEqual(word.used_in_ingame_templates, 0)
        self.assertEqual(word.used_in_onreview_templates, 0)
        self.assertTrue(word.used_in_status.is_NOT_USED)

    def test_update_used_in_status__not_changed(self):
        word = prototypes.WordPrototype.create(self.word_1)

        self.assertEqual(word.used_in_ingame_templates, 0)
        self.assertEqual(word.used_in_onreview_templates, 0)
        self.assertTrue(word.used_in_status.is_NOT_USED)

        word.update_used_in_status(used_in_ingame_templates=0, used_in_onreview_templates=0)

        self.assertEqual(word.used_in_ingame_templates, 0)
        self.assertEqual(word.used_in_onreview_templates, 0)
        self.assertTrue(word.used_in_status.is_NOT_USED)

    def test_update_used_in_status__without_force_update(self):
        word = prototypes.WordPrototype.create(self.word_1)

        word.update_used_in_status(used_in_ingame_templates=1, used_in_onreview_templates=2, force_update=False)

        self.assertEqual(word.used_in_ingame_templates, 1)
        self.assertEqual(word.used_in_onreview_templates, 2)
        self.assertTrue(word.used_in_status.is_IN_INGAME_TEMPLATES)

        word.reload()

        self.assertEqual(word.used_in_ingame_templates, 0)
        self.assertEqual(word.used_in_onreview_templates, 0)
        self.assertTrue(word.used_in_status.is_NOT_USED)

    def test_update_used_in_status__with_force_update(self):
        word = prototypes.WordPrototype.create(self.word_1)

        word.update_used_in_status(used_in_ingame_templates=1, used_in_onreview_templates=2, force_update=True)

        self.assertEqual(word.used_in_ingame_templates, 1)
        self.assertEqual(word.used_in_onreview_templates, 2)
        self.assertTrue(word.used_in_status.is_IN_INGAME_TEMPLATES)

        word.reload()

        self.assertEqual(word.used_in_ingame_templates, 1)
        self.assertEqual(word.used_in_onreview_templates, 2)
        self.assertTrue(word.used_in_status.is_IN_INGAME_TEMPLATES)


class TemplatePrototypeTests(testcase.TestCase):

    def create_template(self, key, word):
        text = '[%(external)s|загл] 1 [%(word)s|%(external)s|буд,вн]' % {'external': key.variables[0].value, 'word': word}

        template = utg_templates.Template()

        template.parse(text, externals=[v.value for v in key.variables])

        return text, template


    def setUp(self):
        super(TemplatePrototypeTests, self).setUp()

        create_test_map()

        self.account_1 = self.accounts_factory.create_account()

        storage.game_dictionary.refresh()

        self.key_1, self.key_2 = random.sample(keys.LEXICON_KEY.records, 2)
        self.word_1 = 'пепельница'
        self.word_2 = 'герой'
        self.text_1, self.template_1 = self.create_template(self.key_1, word=self.word_1)

    def test_create(self):

        restriction_1, restriction_2 = storage.restrictions_storage.all()[:2]

        with mock.patch('the_tale.linguistics.workers.linguistics_manager.Worker.cmd_game_lexicon_changed') as cmd_game_lexicon_changed:
            with self.check_delta(prototypes.TemplatePrototype._db_count, 1):
                prototype = prototypes.TemplatePrototype.create(key=self.key_1,
                                                                raw_template=self.text_1,
                                                                utg_template=self.template_1,
                                                                verificators=[],
                                                                author=self.account_1,
                                                                restrictions=(('hero', restriction_1.id), ('hero', restriction_2.id)))

        self.assertEqual(cmd_game_lexicon_changed.call_count, 1)

        self.assertTrue(prototype.state.is_ON_REVIEW)
        self.assertEqual(self.template_1, prototype.utg_template)
        self.assertEqual(self.text_1, prototype.raw_template)
        self.assertEqual(frozenset((('hero', restriction_1.id), ('hero', restriction_2.id))), prototype.raw_restrictions)

        self.assertTrue(prototype.errors_status.is_HAS_ERRORS)

    def test_update(self):
        prototype = prototypes.TemplatePrototype.create(key=self.key_1, raw_template=self.text_1, utg_template=self.template_1, verificators=[], author=None)

        text, template = self.create_template(self.key_1, word=self.word_2)

        restriction_1, restriction_2, restriction_3 = storage.restrictions_storage.all()[:3]

        with mock.patch('the_tale.linguistics.workers.linguistics_manager.Worker.cmd_game_lexicon_changed') as cmd_game_lexicon_changed:
            with mock.patch('the_tale.linguistics.prototypes.TemplatePrototype.update_errors_status') as update_errors_status:
                prototype.update(raw_template=text,
                                 utg_template=template,
                                 verificators=[prototypes.Verificator(text='test-verificator', externals={}),],
                                 restrictions=(('hero', restriction_1.id), ('level', restriction_2.id), ('hero', restriction_3.id)))

        prototype.reload()

        self.assertEqual(cmd_game_lexicon_changed.call_count, 1)

        self.assertEqual(update_errors_status.call_count, 1)
        self.assertEqual(prototype.raw_template, text)
        self.assertEqual(prototype.raw_restrictions, frozenset((('hero', restriction_1.id), ('level', restriction_2.id), ('hero', restriction_3.id))))

        self.assertEqual(prototype.utg_template, template)

        self.assertEqual(prototype.verificators,
                         [prototypes.Verificator(text='test-verificator', externals={})])

    def test_save(self):
        prototype = prototypes.TemplatePrototype.create(key=self.key_1, raw_template=self.text_1, utg_template=self.template_1, verificators=[], author=self.account_1)
        prototype.utg_template.template = 'xxx'
        prototype.verificators.append(prototypes.Verificator(text='test-verificator', externals={}))

        with mock.patch('the_tale.linguistics.workers.linguistics_manager.Worker.cmd_game_lexicon_changed') as cmd_game_lexicon_changed:
            with mock.patch('the_tale.linguistics.prototypes.TemplatePrototype.update_errors_status') as update_errors_status:
                with self.check_not_changed(prototypes.TemplatePrototype._db_count):
                    prototype.save()

        prototype.reload()

        self.assertEqual(cmd_game_lexicon_changed.call_count, 1)

        self.assertEqual(update_errors_status.call_count, 1)
        self.assertEqual(prototype.utg_template.template, 'xxx')
        self.assertEqual(prototype.verificators,
                         [prototypes.Verificator(text='test-verificator', externals={})])


    def test_get_errors__no_errors(self):
        key = keys.LEXICON_KEY.HERO_COMMON_JOURNAL_LEVEL_UP

        TEXT = '[hero|загл] [level] [неизвестное слово|hero|вн]'

        template = utg_templates.Template()

        template.parse(TEXT, externals=['hero'])

        verificator_1 = prototypes.Verificator(text='Героиня 1 w-1-полнприл,пол,од,ед,вн,жр', externals={'hero': ('героиня', ''), 'level': (1, '')})
        verificator_2 = prototypes.Verificator(text='Рыцари 5 w-1-полнприл,пол,од,мн,вн', externals={'hero': ('рыцарь', 'мн'), 'level': (5, '')})
        verificator_3 = prototypes.Verificator(text='Герой 2 w-1-полнприл,пол,од,ед,вн,мр', externals={'hero': ('герой', ''), 'level': (2, '')})
        verificator_4 = prototypes.Verificator(text='Привидение 5 w-1-полнприл,пол,од,ед,вн,ср', externals={'hero': ('привидение', ''), 'level': (5, '')})

        dictionary = storage.game_dictionary.item

        word = utg_words.Word.create_test_word(type=utg_relations.WORD_TYPE.ADJECTIVE, prefix='w-1-', only_required=True)
        word.forms[0] = 'неизвестное слово'

        dictionary.add_word(word)

        prototype = prototypes.TemplatePrototype.create(key=key,
                                                        raw_template=TEXT,
                                                        utg_template=template,
                                                        verificators=[verificator_1, verificator_2, verificator_3, verificator_4],
                                                        author=self.account_1)

        self.assertTrue(prototype.errors_status.is_NO_ERRORS)

        errors = prototype.get_errors()

        self.assertEqual(errors, [])


    def test_get_errors__no_word_errors(self):
        key = keys.LEXICON_KEY.HERO_COMMON_JOURNAL_LEVEL_UP

        TEXT = '[hero|загл] [level] [неизвестное слово|hero|вн]'

        template = utg_templates.Template()

        template.parse(TEXT, externals=['hero'])

        # verificators with error that would not be returned becouse of words_errors
        verificator_1 = prototypes.Verificator(text='абракадабра', externals={'hero': ('героиня', ''), 'level': (1, '')})
        verificator_2 = prototypes.Verificator(text='Рыцарь 5 w-1-ед,вн', externals={'hero': ('рыцарь', 'мн'), 'level': (5, '')})
        verificator_3 = prototypes.Verificator(text='Герой 2 w-1-ед,вн', externals={'hero': ('герой', ''), 'level': (2, '')})
        verificator_4 = prototypes.Verificator(text='', externals={'hero': ('привидение', ''), 'level': (5, '')})

        prototype = prototypes.TemplatePrototype.create(key=key,
                                                        raw_template=TEXT,
                                                        utg_template=template,
                                                        verificators=[verificator_1, verificator_2, verificator_3, verificator_4],
                                                        author=self.account_1)

        errors = prototype.get_errors()

        self.assertEqual(errors, ['Неизвестное слово: «неизвестное слово»'])

    def test_get_errors__duplicate_word(self):
        key = keys.LEXICON_KEY.HERO_COMMON_JOURNAL_LEVEL_UP

        dictionary = storage.game_dictionary.item

        word_1 = utg_words.Word.create_test_word(type=utg_relations.WORD_TYPE.NOUN, prefix='w-1-', only_required=True)
        word_1.forms[2] = 'дубль'
        self.assertEqual(word_1.form(utg_relations.CASE.DATIVE), 'дубль')

        word_2 = utg_words.Word.create_test_word(type=utg_relations.WORD_TYPE.NOUN, prefix='w-2-', only_required=True)
        word_2.forms[2] = 'дубль'
        self.assertEqual(word_2.form(utg_relations.CASE.DATIVE), 'дубль')

        dictionary.add_word(word_1)
        dictionary.add_word(word_2)

        TEXT = '[hero|загл] [level] [дубль|hero|дт]'

        template = utg_templates.Template()

        template.parse(TEXT, externals=['hero'])

        # verificators with error that would not be returned becouse of words_errors
        verificator_1 = prototypes.Verificator(text='Героиня 1 дубль', externals={'hero': ('героиня', ''), 'level': (1, '')})
        verificator_2 = prototypes.Verificator(text='Рыцари 5 w-1-нс,мн,дт', externals={'hero': ('рыцарь', 'мн'), 'level': (5, '')})
        verificator_3 = prototypes.Verificator(text='Герой 2 дубль', externals={'hero': ('герой', ''), 'level': (2, '')})
        verificator_4 = prototypes.Verificator(text='Привидение 5 дубль', externals={'hero': ('привидение', ''), 'level': (5, '')})

        prototype = prototypes.TemplatePrototype.create(key=key,
                                                        raw_template=TEXT,
                                                        utg_template=template,
                                                        verificators=[verificator_1, verificator_2, verificator_3, verificator_4],
                                                        author=self.account_1)

        errors = prototype.get_errors()

        self.assertEqual(errors, [])


    def test_get_errors__verificators_errors(self):
        key = keys.LEXICON_KEY.HERO_COMMON_JOURNAL_LEVEL_UP

        TEXT = '[hero|загл] [level] [неизвестное слово|hero|вн]'

        template = utg_templates.Template()

        template.parse(TEXT, externals=['hero'])

        verificator_1 = prototypes.Verificator(text='абракадабра', externals={'hero': ('героиня', ''), 'level': (1, '')})
        verificator_2 = prototypes.Verificator(text='Рыцари 5 w-1-полнприл,пол,од,мн,вн', externals={'hero': ('рыцарь', 'мн'), 'level': (5, '')})
        verificator_3 = prototypes.Verificator(text='Герой 2 w-1-ед,вн', externals={'hero': ('герой', ''), 'level': (2, '')})
        verificator_4 = prototypes.Verificator(text='', externals={'hero': ('привидение', ''), 'level': (5, '')})

        dictionary = storage.game_dictionary.item

        word = utg_words.Word.create_test_word(type=utg_relations.WORD_TYPE.ADJECTIVE, prefix='w-1-', only_required=True)
        word.forms[0] = 'неизвестное слово'

        dictionary.add_word(word)

        prototype = prototypes.TemplatePrototype.create(key=key,
                                                        utg_template=template,
                                                        raw_template=TEXT,
                                                        verificators=[verificator_1, verificator_2, verificator_3, verificator_4],
                                                        author=self.account_1)

        errors = prototype.get_errors()

        self.assertEqual(errors, ['Проверочный текст не совпадает с интерпретацией шаблона<br/>Героиня 1 w-1-полнприл,пол,од,ед,вн,жр<br/>абракадабра',
                                  'Проверочный текст не совпадает с интерпретацией шаблона<br/>Герой 2 w-1-полнприл,пол,од,ед,вн,мр<br/>Герой 2 w-1-ед,вн',
                                  'Проверочный текст не совпадает с интерпретацией шаблона<br/>Привидение 5 w-1-полнприл,пол,од,ед,вн,ср<br/>'])


    def test_update_errors_status__without_force_update(self):
        prototype = prototypes.TemplatePrototype.create(key=self.key_1, raw_template=self.text_1, utg_template=self.template_1, verificators=[], author=self.account_1)

        self.assertTrue(prototype.errors_status.is_HAS_ERRORS)

        with mock.patch('the_tale.linguistics.prototypes.TemplatePrototype.has_errors', lambda self: False):
            prototype.update_errors_status(force_update=False)

        self.assertTrue(prototype.errors_status.is_NO_ERRORS)

        prototype.reload()

        self.assertTrue(prototype.errors_status.is_HAS_ERRORS)

    def test_update_errors_status__with_force_update(self):
        prototype = prototypes.TemplatePrototype.create(key=self.key_1, raw_template=self.text_1, utg_template=self.template_1, verificators=[], author=self.account_1)

        self.assertTrue(prototype.errors_status.is_HAS_ERRORS)

        with mock.patch('the_tale.linguistics.prototypes.TemplatePrototype.has_errors', lambda self: False):
            prototype.update_errors_status(force_update=True)

        self.assertTrue(prototype.errors_status.is_NO_ERRORS)

        prototype.reload()

        self.assertTrue(prototype.errors_status.is_NO_ERRORS)


    def test_sync_restrictions(self):
        key = keys.LEXICON_KEY.HERO_COMMON_JOURNAL_LEVEL_UP

        group_1, group_2, group_3 = random.sample(relations.TEMPLATE_RESTRICTION_GROUP.records, 3)

        restriction_1_1 = logic.create_restriction(group=group_1, external_id=100500, name='name-1-1')
        restriction_1_2 = logic.create_restriction(group=group_1, external_id=200500, name='name-1-2')
        restriction_2_1 = logic.create_restriction(group=group_2, external_id=100500, name='name-2-1')
        restriction_2_2 = logic.create_restriction(group=group_2, external_id=200500, name='name-2-2')
        restriction_2_3 = logic.create_restriction(group=group_2, external_id=300500, name='name-2-3')
        restriction_3_1 = logic.create_restriction(group=group_3, external_id=100500, name='name-3-1')

        template_1 = prototypes.TemplatePrototype.create(key=key, raw_template=self.text_1, utg_template=self.template_1,
                                                         verificators=[],  author=self.account_1,
                                                         restrictions=(('hero', restriction_1_1.id), ('hero', restriction_2_2.id)))

        template_2 = prototypes.TemplatePrototype.create(key=key, raw_template=self.text_1, utg_template=self.template_1,
                                                         verificators=[],  author=self.account_1,
                                                         restrictions=(('hero', restriction_1_2.id), ('level', restriction_2_1.id), ('hero', restriction_3_1.id)))

        template_1.update(restrictions=(('level', restriction_2_3.id), ('hero', restriction_2_2.id), ('level', restriction_2_1.id)))

        self.assertEqual(models.TemplateRestriction.objects.count(), 6)

        existed_restrictions = frozenset(models.TemplateRestriction.objects.values_list('template_id', 'variable', 'restriction_id'))

        expected_restrictions = frozenset([(template_1.id, 'hero', restriction_2_2.id),
                                           (template_1.id, 'level', restriction_2_1.id),
                                           (template_1.id, 'level', restriction_2_3.id),
                                           (template_2.id, 'hero', restriction_1_2.id),
                                           (template_2.id, 'level', restriction_2_1.id),
                                           (template_2.id, 'hero', restriction_3_1.id)])

        self.assertEqual(existed_restrictions, expected_restrictions)




class VerificatorTests(testcase.TestCase):

    def setUp(self):
        super(VerificatorTests, self).setUp()
        self.key = keys.LEXICON_KEY.ACTION_FIRST_STEPS_INITIATION

    def test_get_verificators__without_old(self):
        groups = lexicon_logic.get_verificators_groups(key=keys.LEXICON_KEY.HERO_COMMON_JOURNAL_LEVEL_UP, old_groups={})
        self.assertEqual(groups, {'date': (8, 0), 'hero': (0, 0), 'level': (1, 0)})

        verificators = prototypes.Verificator.get_verificators(key=self.key, groups=groups)

        self.assertEqual(len(verificators), 4)

        self.assertEqual(verificators[0], prototypes.Verificator(text='', externals={'date': ('18 сухого месяца 183 года', ''), 'hero': ('герой', ''), 'level': (1, '')}))
        self.assertEqual(verificators[1], prototypes.Verificator(text='', externals={'date': ('18 сухого месяца 183 года', ''), 'hero': ('привидение', ''), 'level': (2, '')}))
        self.assertEqual(verificators[2], prototypes.Verificator(text='', externals={'date': ('18 сухого месяца 183 года', ''), 'hero': ('героиня', ''), 'level': (5, '')}))
        self.assertEqual(verificators[3], prototypes.Verificator(text='', externals={'date': ('18 сухого месяца 183 года', ''), 'hero': ('рыцарь', 'мн'), 'level': (1, '')}))


    def test_get_verificators__with_old(self):
        groups = lexicon_logic.get_verificators_groups(key=keys.LEXICON_KEY.HERO_COMMON_JOURNAL_LEVEL_UP, old_groups={})
        self.assertEqual(groups, {'date': (8, 0), 'hero': (0, 0), 'level': (1, 0)})

        old_verificators = [prototypes.Verificator(text='1', externals={'hero': ('привидение', ''), 'level': (1, '')}),
                            prototypes.Verificator(text='2', externals={'hero': ('героиня', ''), 'level': (1, '')}),
                            prototypes.Verificator(text='3', externals={'hero': ('рыцарь', 'ед'), 'level': (5, '')}),
                            prototypes.Verificator(text='4', externals={'hero': ('абракадабра', ''), 'level': (5, '')}),
                            prototypes.Verificator(text='5', externals={'hero': ('герой', ''), 'level': (2, '')}) ]

        verificators = prototypes.Verificator.get_verificators(key=self.key, groups=groups, old_verificators=old_verificators)

        self.assertEqual(len(verificators), 4)

        self.assertEqual(verificators[0], prototypes.Verificator(text='1', externals={'date': ('18 сухого месяца 183 года', ''), 'hero': ('привидение', ''), 'level': (1, '')}))
        self.assertEqual(verificators[1], prototypes.Verificator(text='5', externals={'date': ('18 сухого месяца 183 года', ''), 'hero': ('герой', ''), 'level': (2, '')}))
        self.assertEqual(verificators[2], prototypes.Verificator(text='', externals={'date': ('18 сухого месяца 183 года', ''), 'hero': ('героиня', ''), 'level': (5, '')}))
        self.assertEqual(verificators[3], prototypes.Verificator(text='', externals={'date': ('18 сухого месяца 183 года', ''), 'hero': ('рыцарь', 'мн'), 'level': (1, '')}))


    def test_get_verificators__one_substitutions_type(self):
        groups = lexicon_logic.get_verificators_groups(key=keys.LEXICON_KEY.PVP_USE_ABILITY_BLOOD, old_groups={})
        self.assertEqual(groups, {'date': (8, 0), 'duelist_1': (0, 0), 'duelist_2': (0, 1), 'effectiveness': (1, 0)})

        verificators = prototypes.Verificator.get_verificators(key=self.key, groups=groups)

        self.assertEqual(len(verificators), 4)

        self.assertEqual(verificators[0], prototypes.Verificator(text='',
                                                                 externals={'date': ('18 сухого месяца 183 года', ''), 'duelist_1': ('герой', ''), 'duelist_2': ('чудовище', ''), 'effectiveness': (1, '')}))
        self.assertEqual(verificators[1], prototypes.Verificator(text='',
                                                                 externals={'date': ('18 сухого месяца 183 года', ''), 'duelist_1': ('привидение', ''), 'duelist_2': ('русалка', ''), 'effectiveness': (2, '')}))
        self.assertEqual(verificators[2], prototypes.Verificator(text='',
                                                                 externals={'date': ('18 сухого месяца 183 года', ''), 'duelist_1': ('героиня', ''), 'duelist_2': ('боец', 'мн'),'effectiveness': (5, '')}))
        self.assertEqual(verificators[3], prototypes.Verificator(text='',
                                                                 externals={'date': ('18 сухого месяца 183 года', ''), 'duelist_1': ('рыцарь', 'мн'), 'duelist_2': ('призрак', ''), 'effectiveness': (1, '')}))



class ContributionTests(testcase.TestCase):

    def setUp(self):
        super(ContributionTests, self).setUp()

        create_test_map()

        self.account_1 = self.accounts_factory.create_account()


    def test_create(self):
        with self.check_delta(prototypes.ContributionPrototype._db_count, 1):
            prototypes.ContributionPrototype.create(type=relations.CONTRIBUTION_TYPE.WORD,
                                                    account_id=self.account_1.id,
                                                    entity_id=1,
                                                    source=relations.CONTRIBUTION_SOURCE.random(),
                                                    state=relations.CONTRIBUTION_STATE.random())


    def test_get_for_or_create(self):
        with self.check_delta(prototypes.ContributionPrototype._db_count, 1):
            prototypes.ContributionPrototype.get_for_or_create(type=relations.CONTRIBUTION_TYPE.WORD,
                                                               account_id=self.account_1.id,
                                                               entity_id=1,
                                                               source=relations.CONTRIBUTION_SOURCE.random(),
                                                               state=relations.CONTRIBUTION_STATE.random())


    def test_create__when_exists(self):
        contribution_1 = prototypes.ContributionPrototype.create(type=relations.CONTRIBUTION_TYPE.WORD,
                                                                 account_id=self.account_1.id,
                                                                 entity_id=1,
                                                                 source=relations.CONTRIBUTION_SOURCE.random(),
                                                                 state=relations.CONTRIBUTION_STATE.random())

        with self.check_not_changed(prototypes.ContributionPrototype._db_count):
            contribution_2 = prototypes.ContributionPrototype.get_for_or_create(type=relations.CONTRIBUTION_TYPE.WORD,
                                                                                account_id=self.account_1.id,
                                                                                entity_id=1,
                                                                                source=contribution_1.source,
                                                                                state=contribution_1.state)

        self.assertEqual(contribution_1.id, contribution_2.id)
