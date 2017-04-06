# coding: utf-8
import random

from unittest import mock

from django.db import IntegrityError, transaction

from utg import templates as utg_templates
from utg import words as utg_words
from utg import relations as utg_relations

from the_tale.common.utils import testcase

from the_tale.game.logic import create_test_map

from .. import prototypes
from .. import relations
from .. import logic
from .. import models
from .. import objects
from .. import storage
from .. import exceptions

from ..lexicon import dictionary as lexicon_dictinonary
from ..lexicon import keys


from the_tale.linguistics.lexicon.groups import relations as groups_relations


class LogicTests(testcase.TestCase):

    def setUp(self):
        super(LogicTests, self).setUp()

        logic.sync_static_restrictions()

        storage.game_dictionary.refresh()
        storage.game_lexicon.refresh()

        self.external_id = random.randint(1, 999)


    def test_get_templates_count(self):
        key_1 = random.choice(keys.LEXICON_KEY.records)
        key_2 = random.choice(keys.LEXICON_KEY.records)

        utg_template_1 = utg_templates.Template()
        utg_template_1.parse('some-text', externals=[v.value for v in key_1.variables])

        utg_template_2 = utg_templates.Template()
        utg_template_2.parse('some-text-2', externals=[v.value for v in key_2.variables])

        template_1_1 = prototypes.TemplatePrototype.create(key=key_1, raw_template='template-1-1', utg_template=utg_template_1, verificators=[], author=None)
        template_1_2 = prototypes.TemplatePrototype.create(key=key_1, raw_template='template-1-2', utg_template=utg_template_1, verificators=[], author=None)

        template_2_1 = prototypes.TemplatePrototype.create(key=key_2, raw_template='template-2-1', utg_template=utg_template_2, verificators=[], author=None)

        template_1_1.state = relations.TEMPLATE_STATE.IN_GAME
        template_1_1.save()

        template_1_2.state = relations.TEMPLATE_STATE.IN_GAME
        template_1_2.save()

        template_2_1.state = relations.TEMPLATE_STATE.IN_GAME
        template_2_1.save()

        groups_count, keys_count = logic.get_templates_count()

        if key_1.group == key_2.group:
            for group in groups_relations.LEXICON_GROUP.records:
                if group == key_1.group:
                    self.assertEqual(groups_count[group], 3)
                else:
                    self.assertEqual(groups_count[group], 0)

        else:
            for group in groups_relations.LEXICON_GROUP.records:
                if group == key_1.group:
                    self.assertEqual(groups_count[group], 2)
                elif group == key_2.group:
                    self.assertEqual(groups_count[group], 1)
                else:
                    self.assertEqual(groups_count[group], 0)


        if key_1 == key_2:
            for key in keys.LEXICON_KEY.records:
                if key == key_1:
                    self.assertEqual(keys_count[key], 3)
                else:
                    self.assertEqual(keys_count[key], 0)
        else:
            for key in keys.LEXICON_KEY.records:
                if key == key_1:
                    self.assertEqual(keys_count[key], 2)
                elif key == key_2:
                    self.assertEqual(keys_count[key], 1)
                else:
                    self.assertEqual(keys_count[key], 0)


    def test_get_text__real(self):

        key = keys.LEXICON_KEY.HERO_COMMON_JOURNAL_LEVEL_UP

        dictionary = storage.game_dictionary.item

        word_1 = utg_words.Word.create_test_word(type=utg_relations.WORD_TYPE.NOUN, prefix='w-3-', only_required=True)
        word_1.forms[3] = 'дубль'
        self.assertEqual(word_1.form(utg_relations.CASE.ACCUSATIVE), 'дубль')

        dictionary.add_word(word_1)

        TEXT = '[hero|загл] [level] [дубль|hero|дт]'

        template = utg_templates.Template()

        template.parse(TEXT, externals=['hero', 'level'])

        prototypes.TemplatePrototype.create(key=key,
                                            raw_template=TEXT,
                                            utg_template=template,
                                            verificators=[],
                                            author=None)

        # update template errors_status and state to enshure, that it will be loaded in game lexicon
        prototypes.TemplatePrototype._db_all().update(errors_status=relations.TEMPLATE_ERRORS_STATUS.NO_ERRORS,
                                                      state=relations.TEMPLATE_STATE.IN_GAME)
        storage.game_lexicon.refresh()

        hero_mock = mock.Mock(utg_name_form=lexicon_dictinonary.DICTIONARY.get_word('герой'), linguistics_restrictions=lambda: [])

        lexicon_key, externals, restrictions = logic.prepair_get_text(key.name,  args={'hero': hero_mock, 'level': 1})

        self.assertIn('date', externals)

        self.assertEqual(logic.render_text(lexicon_key, externals, restrictions),
                         'Герой 1 w-3-нс,ед,дт')


        word_2 = utg_words.Word.create_test_word(type=utg_relations.WORD_TYPE.NOUN, prefix='w-2-', only_required=True)
        word_2.forms[1] = 'дубль'
        self.assertEqual(word_2.form(utg_relations.CASE.GENITIVE), 'дубль')
        dictionary.add_word(word_2)

        lexicon_key, externals, restrictions = logic.prepair_get_text(key.name, args={'hero': hero_mock, 'level': 1})

        self.assertEqual(logic.render_text(lexicon_key, externals, restrictions),
                         'Герой 1 w-2-нс,ед,дт')


    def test_add_word_restrictions_into_variable_restrictions(self):

        key = keys.LEXICON_KEY.HERO_COMMON_JOURNAL_LEVEL_UP

        TEXT = '[hero|загл] [level] [дубль|hero|дт]'

        template = utg_templates.Template()

        template.parse(TEXT, externals=['hero', 'level'])

        prototypes.TemplatePrototype.create(key=key,
                                            raw_template=TEXT,
                                            utg_template=template,
                                            verificators=[],
                                            author=None)

        # update template errors_status and state to enshure, that it will be loaded in game lexicon
        prototypes.TemplatePrototype._db_all().update(errors_status=relations.TEMPLATE_ERRORS_STATUS.NO_ERRORS,
                                                      state=relations.TEMPLATE_STATE.IN_GAME)
        storage.game_lexicon.refresh()

        normal_noun = utg_words.WordForm(utg_words.Word.create_test_word(type=utg_relations.WORD_TYPE.NOUN, prefix='w-1-', only_required=True))
        singular_noun = utg_words.WordForm(utg_words.Word.create_test_word(type=utg_relations.WORD_TYPE.NOUN, prefix='w-1-', only_required=True,
                                                                           properties=utg_words.Properties(utg_relations.NUMBER.SINGULAR)))
        plural_noun = utg_words.WordForm(utg_words.Word.create_test_word(type=utg_relations.WORD_TYPE.NOUN, prefix='w-1-', only_required=True,
                                                                         properties=utg_words.Properties(utg_relations.NUMBER.PLURAL)))

        hero_mock = mock.Mock(utg_name_form=normal_noun, linguistics_restrictions=lambda: [])
        lexicon_key, externals, restrictions = logic.prepair_get_text(key.name,  args={'hero': hero_mock, 'level': 1})
        self.assertIn(('hero', storage.restrictions_storage.get_restriction(relations.TEMPLATE_RESTRICTION_GROUP.PLURAL_FORM,
                                                                            relations.WORD_HAS_PLURAL_FORM.HAS.value).id), restrictions)
        self.assertNotIn(('hero', storage.restrictions_storage.get_restriction(relations.TEMPLATE_RESTRICTION_GROUP.PLURAL_FORM,
                                                                               relations.WORD_HAS_PLURAL_FORM.HAS_NO.value).id), restrictions)

        hero_mock = mock.Mock(utg_name_form=singular_noun, linguistics_restrictions=lambda: [])
        lexicon_key, externals, restrictions = logic.prepair_get_text(key.name,  args={'hero': hero_mock, 'level': 1})
        self.assertNotIn(('hero', storage.restrictions_storage.get_restriction(relations.TEMPLATE_RESTRICTION_GROUP.PLURAL_FORM,
                                                                               relations.WORD_HAS_PLURAL_FORM.HAS.value).id), restrictions)
        self.assertIn(('hero', storage.restrictions_storage.get_restriction(relations.TEMPLATE_RESTRICTION_GROUP.PLURAL_FORM,
                                                                            relations.WORD_HAS_PLURAL_FORM.HAS_NO.value).id), restrictions)

        hero_mock = mock.Mock(utg_name_form=plural_noun, linguistics_restrictions=lambda: [])
        lexicon_key, externals, restrictions = logic.prepair_get_text(key.name,  args={'hero': hero_mock, 'level': 1})
        self.assertIn(('hero', storage.restrictions_storage.get_restriction(relations.TEMPLATE_RESTRICTION_GROUP.PLURAL_FORM,
                                                                            relations.WORD_HAS_PLURAL_FORM.HAS.value).id), restrictions)
        self.assertNotIn(('hero', storage.restrictions_storage.get_restriction(relations.TEMPLATE_RESTRICTION_GROUP.PLURAL_FORM,
                                                                               relations.WORD_HAS_PLURAL_FORM.HAS_NO.value).id), restrictions)


    def test_update_words_usage_info(self):
        word_1 = prototypes.WordPrototype.create(utg_words.Word.create_test_word(type=utg_relations.WORD_TYPE.NOUN, prefix='w-1-', only_required=True))
        word_2 = prototypes.WordPrototype.create(utg_words.Word.create_test_word(type=utg_relations.WORD_TYPE.NOUN, prefix='w-2-', only_required=True))
        word_3 = prototypes.WordPrototype.create(utg_words.Word.create_test_word(type=utg_relations.WORD_TYPE.NOUN, prefix='w-3-', only_required=True))

        key = keys.LEXICON_KEY.HERO_COMMON_JOURNAL_LEVEL_UP

        text_1 = '[w-1-нс,ед,им|hero]'
        text_2 = '[w-1-нс,ед,им|hero] [w-2-нс,ед,им|hero]'

        utg_template = utg_templates.Template()
        utg_template.parse(text_1, externals=['hero', 'level'])
        template = prototypes.TemplatePrototype.create(key=key, raw_template=text_1, utg_template=utg_template, verificators=[], author=None)
        template.state = relations.TEMPLATE_STATE.IN_GAME
        template.save()

        utg_template = utg_templates.Template()
        utg_template.parse(text_2, externals=['hero', 'level'])
        template = prototypes.TemplatePrototype.create(key=key, raw_template=text_2, utg_template=utg_template, verificators=[], author=None)
        self.assertTrue(template.state.is_ON_REVIEW)

        utg_template = utg_templates.Template()
        utg_template.parse(text_2, externals=['hero', 'level'])
        template = prototypes.TemplatePrototype.create(key=key, raw_template=text_2, utg_template=utg_template, verificators=[], author=None)
        self.assertTrue(template.state.is_ON_REVIEW)

        logic.update_words_usage_info()

        word_1.reload()
        word_2.reload()
        word_3.reload()

        self.assertEqual(word_1.used_in_ingame_templates, 1)
        self.assertEqual(word_1.used_in_onreview_templates, 2)
        self.assertTrue(word_1.used_in_status.is_IN_INGAME_TEMPLATES)

        self.assertEqual(word_2.used_in_ingame_templates, 0)
        self.assertEqual(word_2.used_in_onreview_templates, 2)
        self.assertTrue(word_2.used_in_status.is_IN_ONREVIEW_TEMPLATES)

        self.assertEqual(word_3.used_in_ingame_templates, 0)
        self.assertEqual(word_3.used_in_onreview_templates, 0)
        self.assertTrue(word_3.used_in_status.is_NOT_USED)


    def test_update_words_usage_info__ignore_duplicates(self):
        word_1 = prototypes.WordPrototype.create(utg_words.Word.create_test_word(type=utg_relations.WORD_TYPE.NOUN, prefix='w-1-', only_required=True))
        word_2 = prototypes.WordPrototype.create(utg_words.Word.create_test_word(type=utg_relations.WORD_TYPE.NOUN, prefix='w-2-', only_required=True))
        word_3 = prototypes.WordPrototype.create(utg_words.Word.create_test_word(type=utg_relations.WORD_TYPE.NOUN, prefix='w-3-', only_required=True))

        key = keys.LEXICON_KEY.HERO_COMMON_JOURNAL_LEVEL_UP

        word_1.utg_word.forms[1] = word_1.utg_word.forms[0]
        word_1.save()

        text_1 = '[w-1-нс,ед,им|hero]'
        text_2 = '[w-1-нс,ед,им|hero] [w-2-нс,ед,им|hero]'

        utg_template = utg_templates.Template()
        utg_template.parse(text_1, externals=['hero', 'level'])
        template = prototypes.TemplatePrototype.create(key=key, raw_template=text_1, utg_template=utg_template, verificators=[], author=None)
        template.state = relations.TEMPLATE_STATE.IN_GAME
        template.save()

        utg_template = utg_templates.Template()
        utg_template.parse(text_2, externals=['hero', 'level'])
        template = prototypes.TemplatePrototype.create(key=key, raw_template=text_2, utg_template=utg_template, verificators=[], author=None)
        self.assertTrue(template.state.is_ON_REVIEW)

        utg_template = utg_templates.Template()
        utg_template.parse(text_2, externals=['hero', 'level'])
        template = prototypes.TemplatePrototype.create(key=key, raw_template=text_2, utg_template=utg_template, verificators=[], author=None)
        self.assertTrue(template.state.is_ON_REVIEW)

        logic.update_words_usage_info()

        word_1.reload()
        word_2.reload()
        word_3.reload()

        self.assertEqual(word_1.used_in_ingame_templates, 1)
        self.assertEqual(word_1.used_in_onreview_templates, 2)
        self.assertTrue(word_1.used_in_status.is_IN_INGAME_TEMPLATES)

        self.assertEqual(word_2.used_in_ingame_templates, 0)
        self.assertEqual(word_2.used_in_onreview_templates, 2)
        self.assertTrue(word_2.used_in_status.is_IN_ONREVIEW_TEMPLATES)

        self.assertEqual(word_3.used_in_ingame_templates, 0)
        self.assertEqual(word_3.used_in_onreview_templates, 0)
        self.assertTrue(word_3.used_in_status.is_NOT_USED)



    def update_templates_errors(self):
        key = keys.LEXICON_KEY.HERO_COMMON_JOURNAL_LEVEL_UP

        TEXT = '[hero|загл] [level] [неизвестное слово|hero|вн]'

        template = utg_templates.Template()

        template.parse(TEXT, externals=['hero'])

        verificator_1 = prototypes.Verificator(text='Героиня 1 w-1-ед,вн,жр,од,пол', externals={'hero': ('героиня', ''), 'level': (1, '')})
        verificator_2 = prototypes.Verificator(text='Рыцари 5 w-1-мн,вн,од,пол', externals={'hero': ('рыцарь', 'мн'), 'level': (5, '')})
        verificator_3 = prototypes.Verificator(text='Герой 2 w-1-ед,вн,мр,од,пол', externals={'hero': ('герой', ''), 'level': (2, '')})
        verificator_4 = prototypes.Verificator(text='Привидение 5 w-1-ед,вн,ср,од,пол', externals={'hero': ('привидение', ''), 'level': (5, '')})

        dictionary = storage.game_dictionary.item

        word = utg_words.Word.create_test_word(type=utg_relations.WORD_TYPE.ADJECTIVE, prefix='w-1-', only_required=True)
        word.forms[0] = 'неизвестное слово'

        dictionary.add_word(word)

        prototype_1 = prototypes.TemplatePrototype.create(key=key,
                                                        raw_template=TEXT,
                                                        utg_template=template,
                                                        verificators=[verificator_1, verificator_2, verificator_3, verificator_4],
                                                        author=self.account_1)

        prototype_2 = prototypes.TemplatePrototype.create(key=key,
                                                        raw_template=TEXT,
                                                        utg_template=template,
                                                        verificators=[],
                                                        author=self.account_1)

        prototypes.TemplatePrototype._db_filter(id=prototype_1.id).update(errors_status=relations.TEMPLATE_ERRORS_STATUS.HAS_ERRORS)
        prototypes.TemplatePrototype._db_filter(id=prototype_2.id).update(errors_status=relations.TEMPLATE_ERRORS_STATUS.NO_ERRORS)

        prototype_1.reload()
        prototype_2.reload()

        self.assertTrue(prototype_1.errors_status.is_HAS_ERRORS)
        self.assertTrue(prototype_2.errors_status.is_NO_ERRORS)

        logic.update_templates_errors()

        prototype_1.reload()
        prototype_2.reload()

        self.assertTrue(prototype_1.errors_status.is_NO_ERRORS)
        self.assertTrue(prototype_2.errors_status.is_HAS_ERRORS)


    def test_create_restriction(self):

        group = random.choice(relations.TEMPLATE_RESTRICTION_GROUP.records)

        with self.check_delta(models.Restriction.objects.count, 1):
            with self.check_changed(lambda: storage.restrictions_storage._version):
                with self.check_delta(storage.restrictions_storage.__len__, 1):
                    restriction = logic.create_restriction(group=group,
                                                           external_id=self.external_id,
                                                           name='bla-bla-name')

        self.assertEqual(restriction.group, group)
        self.assertEqual(restriction.external_id, self.external_id)
        self.assertEqual(restriction.name, 'bla-bla-name')

        model = models.Restriction.objects.get(id=restriction.id)

        loaded_restriction = objects.Restriction.from_model(model)

        self.assertEqual(loaded_restriction, restriction)


    def test_create_restriction__duplicate(self):

        group = random.choice(relations.TEMPLATE_RESTRICTION_GROUP.records)

        logic.create_restriction(group=group, external_id=self.external_id, name='bla-bla-name')

        with self.check_not_changed(models.Restriction.objects.count):
            with self.check_not_changed(lambda: storage.restrictions_storage._version):
                with self.check_not_changed(storage.restrictions_storage.__len__):
                    with transaction.atomic():
                        self.assertRaises(IntegrityError, logic.create_restriction, group=group,
                                          external_id=self.external_id, name='bla-bla-name')


    def test_sync_static_restrictions(self):
        models.Restriction.objects.all().delete()
        storage.restrictions_storage.refresh()

        for restrictions_group in relations.TEMPLATE_RESTRICTION_GROUP.records:

            if restrictions_group.static_relation is None:
                continue

            for record in restrictions_group.static_relation.records:
                self.assertEqual(storage.restrictions_storage.get_restriction(restrictions_group, record.value), None)


        logic.sync_static_restrictions()

        for restrictions_group in relations.TEMPLATE_RESTRICTION_GROUP.records:

            if restrictions_group.static_relation is None:
                continue

            for record in restrictions_group.static_relation.records:
                self.assertNotEqual(storage.restrictions_storage.get_restriction(restrictions_group, record.value), None)


    def test_sync_restriction__not_exists(self):
        storage.restrictions_storage._get_all_query().delete()
        storage.restrictions_storage.clear()

        group = random.choice(relations.TEMPLATE_RESTRICTION_GROUP.records)

        with self.check_delta(models.Restriction.objects.count, 1):
            with self.check_changed(lambda: storage.restrictions_storage._version):
                with self.check_delta(storage.restrictions_storage.__len__, 1):
                    restriction = logic.sync_restriction(group=group,
                                                         external_id=666,
                                                         name='bla-bla-name')

        self.assertEqual(restriction.group, group)
        self.assertEqual(restriction.external_id, 666)
        self.assertEqual(restriction.name, 'bla-bla-name')

        model = models.Restriction.objects.get(id=restriction.id)

        loaded_restriction = objects.Restriction.from_model(model)

        self.assertEqual(loaded_restriction, restriction)


    def test_sync_restriction__exists(self):
        group = random.choice(relations.TEMPLATE_RESTRICTION_GROUP.records)

        restriction = logic.create_restriction(group=group, external_id=self.external_id, name='bla-bla-name')

        with self.check_not_changed(models.Restriction.objects.count):
            with self.check_changed(lambda: storage.restrictions_storage._version):
                with self.check_not_changed(storage.restrictions_storage.__len__):
                    synced_restriction = logic.sync_restriction(group=group, external_id=self.external_id,
                                                                name='new-name')

        self.assertEqual(synced_restriction.name, 'new-name')

        model = models.Restriction.objects.get(id=restriction.id)

        loaded_restriction = objects.Restriction.from_model(model)

        self.assertEqual(loaded_restriction, synced_restriction)

    def create_removed_template(self):
        TEXT = '[hero|загл] [level] [дубль|hero|дт]'
        utg_template = utg_templates.Template()
        utg_template.parse(TEXT, externals=['hero', 'level'])
        template = prototypes.TemplatePrototype.create(key=keys.LEXICON_KEY.random(),
                                                       raw_template=TEXT,
                                                       utg_template=utg_template,
                                                       verificators=[],
                                                       author=None,
                                                       state=relations.TEMPLATE_STATE.REMOVED)
        return template

    def test_full_remove(self):

        template = self.create_removed_template()

        with self.check_delta(prototypes.TemplatePrototype._db_count, -1):
            logic.full_remove_template(template)

        self.assertEqual(prototypes.TemplatePrototype.get_by_id(template.id), None)


    def test_remove_contributions(self):
        create_test_map()

        template = self.create_removed_template()

        contribution_1 = prototypes.ContributionPrototype.create(type=relations.CONTRIBUTION_TYPE.TEMPLATE,
                                                                 account_id=self.accounts_factory.create_account().id,
                                                                 entity_id=template.id,
                                                                 source=relations.CONTRIBUTION_SOURCE.PLAYER,
                                                                 state=relations.CONTRIBUTION_STATE.ON_REVIEW)

        contribution_2 = prototypes.ContributionPrototype.create(type=relations.CONTRIBUTION_TYPE.TEMPLATE,
                                                                 account_id=self.accounts_factory.create_account().id,
                                                                 entity_id=template.id,
                                                                 source=relations.CONTRIBUTION_SOURCE.PLAYER,
                                                                 state=relations.CONTRIBUTION_STATE.IN_GAME)

        with self.check_delta(prototypes.TemplatePrototype._db_count, -1):
            logic.full_remove_template(template)

        self.assertFalse(prototypes.ContributionPrototype._db_filter(id=contribution_1.id).exists())
        self.assertTrue(prototypes.ContributionPrototype._db_filter(id=contribution_2.id).exists())


    def test_get_text__no_key(self):
        hero_mock = mock.Mock(utg_name_form=lexicon_dictinonary.DICTIONARY.get_word('герой'), linguistics_restrictions=lambda: [])
        self.assertRaises(exceptions.NoLexiconKeyError, logic.get_text, 'wrong_key', args={'hero': hero_mock, 'level': 1}, quiet=False)
        self.assertEqual(logic.get_text('wrong_key', args={'hero': hero_mock, 'level': 1}, quiet=True), None)


    def test_get_text__no_templates(self):
        key = random.choice(keys.LEXICON_KEY.records)
        hero_mock = mock.Mock(utg_name_form=lexicon_dictinonary.DICTIONARY.get_word('герой'), linguistics_restrictions=lambda: [])
        args = {'hero': hero_mock, 'level': 1}

        self.assertEqual(logic.get_text(key.name, args=args),
                         logic.fake_text(key.name, logic.prepair_get_text(key.name, args)[1]))


    def test_get_word_restrictions(self):

        normal_noun = utg_words.WordForm(utg_words.Word.create_test_word(type=utg_relations.WORD_TYPE.NOUN, prefix='w-1-', only_required=True))
        singular_noun = utg_words.WordForm(utg_words.Word.create_test_word(type=utg_relations.WORD_TYPE.NOUN, prefix='w-1-', only_required=True,
                                                                           properties=utg_words.Properties(utg_relations.NUMBER.SINGULAR)))
        plural_noun = utg_words.WordForm(utg_words.Word.create_test_word(type=utg_relations.WORD_TYPE.NOUN, prefix='w-1-', only_required=True,
                                                                         properties=utg_words.Properties(utg_relations.NUMBER.PLURAL)))

        self.assertEqual(logic.get_word_restrictions('x', normal_noun), (('x', storage.restrictions_storage.get_restriction(relations.TEMPLATE_RESTRICTION_GROUP.PLURAL_FORM,
                                                                                                                            relations.WORD_HAS_PLURAL_FORM.HAS.value).id),))
        self.assertEqual(logic.get_word_restrictions('x', singular_noun), (('x', storage.restrictions_storage.get_restriction(relations.TEMPLATE_RESTRICTION_GROUP.PLURAL_FORM,
                                                                                                                              relations.WORD_HAS_PLURAL_FORM.HAS_NO.value).id),))
        self.assertEqual(logic.get_word_restrictions('x', plural_noun), (('x', storage.restrictions_storage.get_restriction(relations.TEMPLATE_RESTRICTION_GROUP.PLURAL_FORM,
                                                                                                                            relations.WORD_HAS_PLURAL_FORM.HAS.value).id),))
