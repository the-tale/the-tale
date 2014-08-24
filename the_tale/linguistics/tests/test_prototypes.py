# coding: utf-8

import random

from utg import relations as utg_relations
from utg import words as utg_words

from the_tale.common.utils.testcase import TestCase

from the_tale.linguistics import prototypes
from the_tale.linguistics import relations


class WordPrototypeTests(TestCase):

    def setUp(self):
        super(WordPrototypeTests, self).setUp()
        self.word_type_1, self.word_type_2 = random.sample(utg_relations.WORD_TYPE.records, 2)
        self.word_1 = utg_words.Word.create_test_word(self.word_type_1)

    def test_create(self):

        with self.check_delta(prototypes.WordPrototype._db_count, 1):
            prototype = prototypes.WordPrototype.create(self.word_1)

        self.assertTrue(prototype.state.is_ON_REVIEW)
        self.assertEqual(self.word_1, prototype.utg_word)
        self.assertEqual(self.word_1.normal_form(), prototype.utg_word.normal_form())


    def test_save(self):
        prototype = prototypes.WordPrototype.create(self.word_1)
        prototype.utg_word.forms[0] = u'xxx'

        with self.check_not_changed(prototypes.WordPrototype._db_count):
            prototype.save()

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
