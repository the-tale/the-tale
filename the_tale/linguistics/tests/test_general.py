# coding: utf-8
import collections

from django.db import IntegrityError
from django.db import transaction

from utg import relations as utg_relations

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
                    self.assertTrue(lexicon_dictinonary.DICTIONARY.has_words(word, verificator.utg_type))


    def test_all_lexicon_keys_have_suffient_number_of_verificator_substitutions(self):

        for key in keys.LEXICON_KEY.records:
            verificators = collections.Counter(v.verificator for v in key.variables)
            for verificator, number in verificators.iteritems():
                self.assertTrue(len(verificator.substitutions) >= number)
