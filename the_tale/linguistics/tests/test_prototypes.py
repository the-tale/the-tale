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
        prototype.utg_word.forms[0] = u'xxx'


        with mock.patch('the_tale.linguistics.workers.linguistics_manager.Worker.cmd_game_dictionary_changed') as cmd_game_dictionary_changed:
            with mock.patch('the_tale.linguistics.storage.game_dictionary.refresh') as game_refresh:
                with self.check_not_changed(lambda: storage.game_dictionary.version):
                    with self.check_not_changed(prototypes.WordPrototype._db_count):
                        prototype.save()

        self.assertEqual(game_refresh.call_count, 0)
        self.assertEqual(cmd_game_dictionary_changed.call_count, 1)

        prototype.reload()
        self.assertEqual(prototype.utg_word.forms[0], u'xxx')


    def test_save__in_game(self):
        prototype = prototypes.WordPrototype.create(self.word_1)
        prototype.utg_word.forms[0] = u'xxx'
        prototype.state = relations.WORD_STATE.IN_GAME

        with mock.patch('the_tale.linguistics.storage.game_dictionary.refresh') as game_refresh:
            with self.check_changed(lambda: storage.game_dictionary.version):
                with self.check_not_changed(prototypes.WordPrototype._db_count):
                    prototype.save()

        self.assertEqual(game_refresh.call_count, 1)

        prototype.reload()
        self.assertEqual(prototype.utg_word.forms[0], u'xxx')

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
        text = u'[%(external)s|загл] 1 [%(word)s|%(external)s|буд,вн]' % {'external': key.variables[0].value, 'word': word}

        template = utg_templates.Template()

        template.parse(text, externals=[v.value for v in key.variables])

        return text, template


    def setUp(self):
        super(TemplatePrototypeTests, self).setUp()

        create_test_map()

        result, account_id, bundle_id = register_user('test_user1', 'test_user_1@test.com', '111111')
        self.account_1 = AccountPrototype.get_by_id(account_id)

        storage.game_dictionary.refresh()

        self.key_1, self.key_2 = random.sample(keys.LEXICON_KEY.records, 2)
        self.word_1 = u'пепельница'
        self.word_2 = u'герой'
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
                                 verificators=[prototypes.Verificator(text=u'test-verificator', externals={}),],
                                 restrictions=(('hero', restriction_1.id), ('level', restriction_2.id), ('hero', restriction_3.id)))

        prototype.reload()

        self.assertEqual(cmd_game_lexicon_changed.call_count, 1)

        self.assertEqual(update_errors_status.call_count, 1)
        self.assertEqual(prototype.raw_template, text)
        self.assertEqual(prototype.raw_restrictions, frozenset((('hero', restriction_1.id), ('level', restriction_2.id), ('hero', restriction_3.id))))

        self.assertEqual(prototype.utg_template, template)

        self.assertEqual(prototype.verificators,
                         [prototypes.Verificator(text=u'test-verificator', externals={})])

    def test_save(self):
        prototype = prototypes.TemplatePrototype.create(key=self.key_1, raw_template=self.text_1, utg_template=self.template_1, verificators=[], author=self.account_1)
        prototype.utg_template.template = u'xxx'
        prototype.verificators.append(prototypes.Verificator(text=u'test-verificator', externals={}))

        with mock.patch('the_tale.linguistics.workers.linguistics_manager.Worker.cmd_game_lexicon_changed') as cmd_game_lexicon_changed:
            with mock.patch('the_tale.linguistics.prototypes.TemplatePrototype.update_errors_status') as update_errors_status:
                with self.check_not_changed(prototypes.TemplatePrototype._db_count):
                    prototype.save()

        prototype.reload()

        self.assertEqual(cmd_game_lexicon_changed.call_count, 1)

        self.assertEqual(update_errors_status.call_count, 1)
        self.assertEqual(prototype.utg_template.template, u'xxx')
        self.assertEqual(prototype.verificators,
                         [prototypes.Verificator(text=u'test-verificator', externals={})])


    def test_get_errors__no_errors(self):
        key = keys.LEXICON_KEY.HERO_COMMON_JOURNAL_LEVEL_UP

        TEXT = u'[hero|загл] [level] [неизвестное слово|hero|вн]'

        template = utg_templates.Template()

        template.parse(TEXT, externals=['hero'])

        verificator_1 = prototypes.Verificator(text=u'Героиня 1 w-1-полнприл,ед,вн,жр,од,пол', externals={'hero': (u'героиня', u''), 'level': (1, u'')})
        verificator_2 = prototypes.Verificator(text=u'Рыцари 5 w-1-полнприл,мн,вн,од,пол', externals={'hero': (u'рыцарь', u'мн'), 'level': (5, u'')})
        verificator_3 = prototypes.Verificator(text=u'Герой 2 w-1-полнприл,ед,вн,мр,од,пол', externals={'hero': (u'герой', u''), 'level': (2, u'')})
        verificator_4 = prototypes.Verificator(text=u'Привидение 5 w-1-полнприл,ед,вн,ср,од,пол', externals={'hero': (u'привидение', u''), 'level': (5, u'')})

        dictionary = storage.game_dictionary.item

        word = utg_words.Word.create_test_word(type=utg_relations.WORD_TYPE.ADJECTIVE, prefix=u'w-1-', only_required=True)
        word.forms[0] = u'неизвестное слово'

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

        errors = prototype.get_errors()

        self.assertEqual(errors, [u'Неизвестное слово: «неизвестное слово»'])

    def test_get_errors__duplicate_word(self):
        key = keys.LEXICON_KEY.HERO_COMMON_JOURNAL_LEVEL_UP

        dictionary = storage.game_dictionary.item

        word_1 = utg_words.Word.create_test_word(type=utg_relations.WORD_TYPE.NOUN, prefix=u'w-1-', only_required=True)
        word_1.forms[2] = u'дубль'
        self.assertEqual(word_1.form(utg_relations.CASE.DATIVE), u'дубль')

        word_2 = utg_words.Word.create_test_word(type=utg_relations.WORD_TYPE.NOUN, prefix=u'w-2-', only_required=True)
        word_2.forms[2] = u'дубль'
        self.assertEqual(word_2.form(utg_relations.CASE.DATIVE), u'дубль')

        dictionary.add_word(word_1)
        dictionary.add_word(word_2)

        TEXT = u'[hero|загл] [level] [дубль|hero|дт]'

        template = utg_templates.Template()

        template.parse(TEXT, externals=['hero'])

        # verificators with error that would not be returned becouse of words_errors
        verificator_1 = prototypes.Verificator(text=u'Героиня 1 дубль', externals={'hero': (u'героиня', u''), 'level': (1, u'')})
        verificator_2 = prototypes.Verificator(text=u'Рыцари 5 w-1-нс,мн,дт', externals={'hero': (u'рыцарь', u'мн'), 'level': (5, u'')})
        verificator_3 = prototypes.Verificator(text=u'Герой 2 дубль', externals={'hero': (u'герой', u''), 'level': (2, u'')})
        verificator_4 = prototypes.Verificator(text=u'Привидение 5 дубль', externals={'hero': (u'привидение', u''), 'level': (5, u'')})

        prototype = prototypes.TemplatePrototype.create(key=key,
                                                        raw_template=TEXT,
                                                        utg_template=template,
                                                        verificators=[verificator_1, verificator_2, verificator_3, verificator_4],
                                                        author=self.account_1)

        errors = prototype.get_errors()

        self.assertEqual(errors, [])


    def test_get_errors__verificators_errors(self):
        key = keys.LEXICON_KEY.HERO_COMMON_JOURNAL_LEVEL_UP

        TEXT = u'[hero|загл] [level] [неизвестное слово|hero|вн]'

        template = utg_templates.Template()

        template.parse(TEXT, externals=['hero'])

        verificator_1 = prototypes.Verificator(text=u'абракадабра', externals={'hero': (u'героиня', u''), 'level': (1, u'')})
        verificator_2 = prototypes.Verificator(text=u'Рыцари 5 w-1-полнприл,мн,вн,од,пол', externals={'hero': (u'рыцарь', u'мн'), 'level': (5, u'')})
        verificator_3 = prototypes.Verificator(text=u'Герой 2 w-1-ед,вн', externals={'hero': (u'герой', u''), 'level': (2, u'')})
        verificator_4 = prototypes.Verificator(text=u'', externals={'hero': (u'привидение', u''), 'level': (5, u'')})

        dictionary = storage.game_dictionary.item

        word = utg_words.Word.create_test_word(type=utg_relations.WORD_TYPE.ADJECTIVE, prefix=u'w-1-', only_required=True)
        word.forms[0] = u'неизвестное слово'

        dictionary.add_word(word)

        prototype = prototypes.TemplatePrototype.create(key=key,
                                                        utg_template=template,
                                                        raw_template=TEXT,
                                                        verificators=[verificator_1, verificator_2, verificator_3, verificator_4],
                                                        author=self.account_1)

        errors = prototype.get_errors()

        self.assertEqual(errors, [u'Проверочный текст не совпадает с интерпретацией шаблона<br/>Героиня 1 w-1-полнприл,ед,вн,жр,од,пол<br/>абракадабра',
                                  u'Проверочный текст не совпадает с интерпретацией шаблона<br/>Герой 2 w-1-полнприл,ед,вн,мр,од,пол<br/>Герой 2 w-1-ед,вн',
                                  u'Проверочный текст не совпадает с интерпретацией шаблона<br/>Привидение 5 w-1-полнприл,ед,вн,ср,од,пол<br/>'])


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

        restriction_1_1 = logic.create_restriction(group=group_1, external_id=100500, name=u'name-1-1')
        restriction_1_2 = logic.create_restriction(group=group_1, external_id=200500, name=u'name-1-2')
        restriction_2_1 = logic.create_restriction(group=group_2, external_id=100500, name=u'name-2-1')
        restriction_2_2 = logic.create_restriction(group=group_2, external_id=200500, name=u'name-2-2')
        restriction_2_3 = logic.create_restriction(group=group_2, external_id=300500, name=u'name-2-3')
        restriction_3_1 = logic.create_restriction(group=group_3, external_id=100500, name=u'name-3-1')

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


class ContributionTests(testcase.TestCase):

    def setUp(self):
        super(ContributionTests, self).setUp()

        create_test_map()

        result, account_id, bundle_id = register_user('test_user1', 'test_user1@test.com', '111111')
        self.account_1 = AccountPrototype.get_by_id(account_id)



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
                                                                                source=relations.CONTRIBUTION_SOURCE.random(),
                                                                                state=relations.CONTRIBUTION_STATE.random())

        self.assertEqual(contribution_1.id, contribution_2.id)
