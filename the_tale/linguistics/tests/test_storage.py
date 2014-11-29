# coding: utf-8
import random

from utg import relations as utg_relations
from utg import words as utg_words
from utg import templates as utg_templates

from the_tale.common.utils.testcase import TestCase

from the_tale.linguistics import prototypes
from the_tale.linguistics import relations
from the_tale.linguistics import storage
from the_tale.linguistics import logic

from the_tale.linguistics.lexicon import keys


class DictionaryStoragesTests(TestCase):

    def setUp(self):
        super(DictionaryStoragesTests, self).setUp()
        self.word_type_1, self.word_type_2, self.word_type_3 = random.sample([t for t in utg_relations.WORD_TYPE.records if not t.is_INTEGER and not t.is_TEXT], 3)

        self.utg_word_1 = utg_words.Word.create_test_word(self.word_type_1, prefix='w1-')
        self.utg_word_2_1 = utg_words.Word.create_test_word(self.word_type_2, prefix='w2_1-')
        self.utg_word_3 = utg_words.Word.create_test_word(self.word_type_3, prefix='w3-')
        self.utg_word_2_2 = utg_words.Word.create_test_word(self.word_type_2, prefix='w2_2-')

        self.utg_word_2_2.forms = [f if f[4:] != self.utg_word_2_1.normal_form()[4:] else self.utg_word_2_1.normal_form() for f in self.utg_word_2_2.forms]

        self.word_1 = prototypes.WordPrototype.create(self.utg_word_1)
        self.word_2_1 = prototypes.WordPrototype.create(self.utg_word_2_1)
        self.word_3 = prototypes.WordPrototype.create(self.utg_word_3)

        self.word_2_1.state = relations.WORD_STATE.IN_GAME
        self.word_2_1.save()

        self.word_3.state = relations.WORD_STATE.IN_GAME
        self.word_3.save()

        self.word_2_2 = prototypes.WordPrototype.create(self.utg_word_2_2)


    def check_word_in_dictionary(self, dictionary, word, result):
        if not dictionary.has_word(word.normal_form()):
            self.assertFalse(result)
            return

        self.assertEqual(word.forms == dictionary.get_word(word.normal_form()).word.forms, result)


    def test_game_dictionary(self):
        dictionary = storage.game_dictionary.item

        self.check_word_in_dictionary(dictionary, self.utg_word_1, False)
        self.check_word_in_dictionary(dictionary, self.utg_word_2_1, True)
        self.check_word_in_dictionary(dictionary, self.utg_word_3, True)
        self.check_word_in_dictionary(dictionary, self.utg_word_2_2, False)



class LexiconStoragesTests(TestCase):

    def setUp(self):
        super(LexiconStoragesTests, self).setUp()


    def test_templates_query(self):
        key = keys.LEXICON_KEY.HERO_COMMON_JOURNAL_LEVEL_UP

        text = u'[w-1-ед,им|hero]'

        utg_template = utg_templates.Template()
        utg_template.parse(text, externals=['hero', 'level'])
        template_1 = prototypes.TemplatePrototype.create(key=key, raw_template=text, utg_template=utg_template, verificators=[], author=None)
        template_2 = prototypes.TemplatePrototype.create(key=key, raw_template=text, utg_template=utg_template, verificators=[], author=None)
        template_3 = prototypes.TemplatePrototype.create(key=key, raw_template=text, utg_template=utg_template, verificators=[], author=None)

        prototypes.TemplatePrototype._db_filter(id__in=[template_1.id, template_2.id]).update(state=relations.TEMPLATE_STATE.IN_GAME)

        self.assertEqual(storage.game_lexicon._templates_query().count(), 0)

        prototypes.TemplatePrototype._db_filter(id=template_2.id).update(errors_status=relations.TEMPLATE_ERRORS_STATUS.NO_ERRORS)

        self.assertEqual(storage.game_lexicon._templates_query().count(), 1)

        prototypes.TemplatePrototype._db_filter(id=template_3.id).update(errors_status=relations.TEMPLATE_ERRORS_STATUS.NO_ERRORS)

        self.assertEqual(storage.game_lexicon._templates_query().count(), 1)


class RestrictionsStorageTests(TestCase):

    def setUp(self):
        super(RestrictionsStorageTests, self).setUp()


    def test_clear(self):
        self.assertEqual(storage.restrictions_storage._data, {})
        self.assertEqual(storage.restrictions_storage._restrictions, {})
        self.assertEqual(storage.restrictions_storage._restrictions_by_group, {})


    def test_add_item(self):
        restriction_1 = logic.create_restriction(group=relations.TEMPLATE_RESTRICTION_GROUP.RACE, external_id=666, name=u'bla-bla-name')

        self.assertEqual(storage.restrictions_storage._data, {restriction_1.id: restriction_1})
        self.assertEqual(storage.restrictions_storage._restrictions, {restriction_1.storage_key(): restriction_1})
        self.assertEqual(storage.restrictions_storage._restrictions_by_group, {restriction_1.group: [restriction_1]})

        restriction_2 = logic.create_restriction(group=relations.TEMPLATE_RESTRICTION_GROUP.GENDER, external_id=667, name=u'name-2')
        restriction_3 = logic.create_restriction(group=relations.TEMPLATE_RESTRICTION_GROUP.RACE, external_id=668, name=u'name-3')

        self.assertEqual(storage.restrictions_storage._data, {restriction_1.id: restriction_1,
                                                              restriction_2.id: restriction_2,
                                                              restriction_3.id: restriction_3})
        self.assertEqual(storage.restrictions_storage._restrictions, {restriction_1.storage_key(): restriction_1,
                                                                      restriction_2.storage_key(): restriction_2,
                                                                      restriction_3.storage_key(): restriction_3})
        self.assertEqual(storage.restrictions_storage._restrictions_by_group, {restriction_1.group: [restriction_1, restriction_3],
                                                                               restriction_2.group: [restriction_2]})


    def test_get_restriction(self):
        restriction_1 = logic.create_restriction(group=relations.TEMPLATE_RESTRICTION_GROUP.RACE, external_id=666, name=u'bla-bla-name')
        restriction_2 = logic.create_restriction(group=relations.TEMPLATE_RESTRICTION_GROUP.GENDER, external_id=667, name=u'name-2')
        restriction_3 = logic.create_restriction(group=relations.TEMPLATE_RESTRICTION_GROUP.RACE, external_id=668, name=u'name-3')

        self.assertEqual(restriction_1, storage.restrictions_storage.get_restriction(relations.TEMPLATE_RESTRICTION_GROUP.RACE, 666))
        self.assertEqual(restriction_2, storage.restrictions_storage.get_restriction(relations.TEMPLATE_RESTRICTION_GROUP.GENDER, 667))
        self.assertEqual(restriction_3, storage.restrictions_storage.get_restriction(relations.TEMPLATE_RESTRICTION_GROUP.RACE, 668))


    def test_get_restrictions(self):
        restriction_1 = logic.create_restriction(group=relations.TEMPLATE_RESTRICTION_GROUP.RACE, external_id=666, name=u'bla-bla-name')
        restriction_2 = logic.create_restriction(group=relations.TEMPLATE_RESTRICTION_GROUP.GENDER, external_id=667, name=u'name-2')
        restriction_3 = logic.create_restriction(group=relations.TEMPLATE_RESTRICTION_GROUP.RACE, external_id=668, name=u'name-3')

        self.assertEqual(storage.restrictions_storage.get_restrictions(relations.TEMPLATE_RESTRICTION_GROUP.RACE), [restriction_1, restriction_3])
        self.assertEqual(storage.restrictions_storage.get_restrictions(relations.TEMPLATE_RESTRICTION_GROUP.GENDER), [restriction_2])
