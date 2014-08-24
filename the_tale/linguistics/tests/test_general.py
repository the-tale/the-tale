# coding: utf-8

from django.db import IntegrityError
from django.db import transaction

from utg import relations as utg_relations

from the_tale.common.utils.testcase import TestCase

from the_tale.linguistics import models
from the_tale.linguistics import relations


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
