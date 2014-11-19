# coding: utf-8
import collections

from django.db import IntegrityError
from django.db import transaction

from utg import words as utg_words
from utg import relations as utg_relations
from utg import data as utg_data

from the_tale.common.utils.testcase import TestCase

from the_tale.linguistics import models
from the_tale.linguistics import relations

from the_tale.linguistics.lexicon import relations as lexicon_relations
from the_tale.linguistics.lexicon import dictionary as lexicon_dictinonary
from the_tale.linguistics.lexicon import keys


class GeneralTests(TestCase):

    def setUp(self):
        super(GeneralTests, self).setUp()

    def get_uniqueness_data(self, type=None, state=None, normal_form=None):
        if state is None:
            state = relations.WORD_STATE.ON_REVIEW
        if normal_form is None:
            normal_form = 'normal-form'

        return {'type': type,
                'state': state,
                'normal_form': normal_form,
                'forms': u'' }

    def test_uniqueness(self):
        type_1 = utg_relations.WORD_TYPE.records[0]
        type_2 = utg_relations.WORD_TYPE.records[1]

        models.Word.objects.create(**self.get_uniqueness_data(type=type_1))

        with transaction.atomic():
            self.assertRaises(IntegrityError, models.Word.objects.create, **self.get_uniqueness_data())

        models.Word.objects.create(**self.get_uniqueness_data(type=type_2))
        models.Word.objects.create(**self.get_uniqueness_data(type=type_1, normal_form='normal_form-2'))
        models.Word.objects.create(**self.get_uniqueness_data(type=type_1, state=relations.WORD_STATE.IN_GAME))

        with transaction.atomic():
            self.assertRaises(IntegrityError, models.Word.objects.create, **self.get_uniqueness_data(type=type_2))

        with transaction.atomic():
            self.assertRaises(IntegrityError, models.Word.objects.create, **self.get_uniqueness_data(type=type_1, normal_form='normal_form-2'))

        with transaction.atomic():
            self.assertRaises(IntegrityError, models.Word.objects.create, **self.get_uniqueness_data(type=type_1, state=relations.WORD_STATE.IN_GAME))


    def test_all_lexicon_verificators_in_dictionary(self):
        for verificator in lexicon_relations.VARIABLE_VERIFICATOR.records:
            if verificator.utg_type is None:
                continue
            for substitutions in verificator.substitutions:
                for word, properties in substitutions:
                    self.assertTrue(isinstance(word, (int, long)) or lexicon_dictinonary.DICTIONARY.has_word(word))


    def test_all_lexicon_keys_have_suffient_number_of_verificator_substitutions(self):

        for key in keys.LEXICON_KEY.records:
            verificators = collections.Counter(v.verificator for v in key.variables)
            for verificator, number in verificators.iteritems():
                self.assertTrue(len(verificator.substitutions) >= number)


    def test_correct_autofill_of_noun_countable_form(self):
        word = utg_words.Word.create_test_word(utg_relations.WORD_TYPE.NOUN)

        for key, index in utg_data.WORDS_CACHES[word.type].iteritems():
            if utg_relations.NOUN_FORM.COUNTABLE in key:
                word.forms[index] = u''

        word.autofill_missed_forms()

        for key, index in utg_data.WORDS_CACHES[word.type].iteritems():
            if utg_relations.NOUN_FORM.COUNTABLE in key:
                modified_key = list(property if property != utg_relations.NOUN_FORM.COUNTABLE else utg_relations.NOUN_FORM.NORMAL for property in key)
                self.assertEqual(word.form(utg_words.Properties(*key)),
                                 word.form(utg_words.Properties(*modified_key)))
