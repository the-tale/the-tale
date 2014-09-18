# coding: utf-8

import random

from utg import relations as utg_relations
from utg import words as utg_words

from the_tale.common.utils.testcase import TestCase

from the_tale.linguistics import prototypes
from the_tale.linguistics import relations
from the_tale.linguistics import storage



class DictionaryStoragesTests(TestCase):

    def setUp(self):
        super(DictionaryStoragesTests, self).setUp()
        self.word_type_1, self.word_type_2, self.word_type_3 = random.sample([t for t in utg_relations.WORD_TYPE.records if not t.is_INTEGER], 3)
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

        storage.raw_dictionary.refresh()
        storage.game_dictionary.refresh()


    def check_word_in_dictionary(self, dictionary, word, result):
        self.assertEqual(any(word.forms == w.word.forms for w in dictionary.get_words(word.normal_form(), type=word.type)), result)


    def test_game_dictionary(self):
        dictionary = storage.game_dictionary.item

        self.check_word_in_dictionary(dictionary, self.utg_word_1, False)
        self.check_word_in_dictionary(dictionary, self.utg_word_2_1, True)
        self.check_word_in_dictionary(dictionary, self.utg_word_3, True)
        self.check_word_in_dictionary(dictionary, self.utg_word_2_2, False)


    def test_raw_dictionary(self):
        dictionary = storage.raw_dictionary.item

        self.check_word_in_dictionary(dictionary, self.utg_word_1, True)
        self.check_word_in_dictionary(dictionary, self.utg_word_2_1, False)
        self.check_word_in_dictionary(dictionary, self.utg_word_3, True)
        self.check_word_in_dictionary(dictionary, self.utg_word_2_2, True)
