# coding: utf-8
import random

from utg import templates as utg_templates
from utg import words as utg_words
from utg import relations as utg_relations

from the_tale.common.utils.testcase import TestCase

from the_tale.linguistics import prototypes
from the_tale.linguistics import relations
from the_tale.linguistics import logic

from the_tale.linguistics.lexicon import dictionary as lexicon_dictinonary
from the_tale.linguistics.lexicon import keys
from the_tale.linguistics import storage

from the_tale.linguistics.lexicon.groups import relations as groups_relations


class LogicTests(TestCase):

    def setUp(self):
        super(LogicTests, self).setUp()

        storage.game_dictionary.refresh()
        storage.game_lexicon.refresh()


    def test_get_templates_count(self):
        key_1 = random.choice(keys.LEXICON_KEY.records)
        key_2 = random.choice(keys.LEXICON_KEY.records)

        utg_template_1 = utg_templates.Template()
        utg_template_1.parse(u'some-text', externals=[v.value for v in key_1.variables])

        utg_template_2 = utg_templates.Template()
        utg_template_2.parse(u'some-text-2', externals=[v.value for v in key_2.variables])

        template_1_1 = prototypes.TemplatePrototype.create(key=key_1, raw_template=u'template-1-1', utg_template=utg_template_1, verificators=[], author=None)
        template_1_2 = prototypes.TemplatePrototype.create(key=key_1, raw_template=u'template-1-2', utg_template=utg_template_1, verificators=[], author=None)

        template_2_1 = prototypes.TemplatePrototype.create(key=key_2, raw_template=u'template-2-1', utg_template=utg_template_2, verificators=[], author=None)

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

        word_1 = utg_words.Word.create_test_word(type=utg_relations.WORD_TYPE.NOUN, prefix=u'w-1-', only_required=True)
        word_1.forms[2] = u'дубль'
        self.assertEqual(word_1.form(utg_relations.CASE.DATIVE), u'дубль')

        dictionary.add_word(word_1)

        TEXT = u'[hero|загл] [level] [дубль|hero|дт]'

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

        self.assertEqual(logic._get_text__real('tests', key.name, args={'hero': lexicon_dictinonary.DICTIONARY.get_word(u'герой'), 'level': 1}),
                         u'Герой 1 дубль')


        word_2 = utg_words.Word.create_test_word(type=utg_relations.WORD_TYPE.NOUN, prefix=u'w-2-', only_required=True)
        word_2.forms[2] = u'дубль'
        self.assertEqual(word_2.form(utg_relations.CASE.DATIVE), u'дубль')
        dictionary.add_word(word_2)

        self.assertEqual(logic._get_text__real('tests', key.name, args={'hero': lexicon_dictinonary.DICTIONARY.get_word(u'герой'), 'level': 1}, quiet=True),
                         None)


    def test_update_words_usage_info(self):
        word_1 = prototypes.WordPrototype.create(utg_words.Word.create_test_word(type=utg_relations.WORD_TYPE.NOUN, prefix=u'w-1-', only_required=True))
        word_2 = prototypes.WordPrototype.create(utg_words.Word.create_test_word(type=utg_relations.WORD_TYPE.NOUN, prefix=u'w-2-', only_required=True))
        word_3 = prototypes.WordPrototype.create(utg_words.Word.create_test_word(type=utg_relations.WORD_TYPE.NOUN, prefix=u'w-3-', only_required=True))

        key = keys.LEXICON_KEY.HERO_COMMON_JOURNAL_LEVEL_UP

        text_1 = u'[w-1-ед,им|hero]'
        text_2 = u'[w-1-ед,им|hero] [w-2-ед,им|hero]'

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
