# coding: utf-8
import mock

from the_tale.common.utils.testcase import TestCase

from the_tale.linguistics.lexicon import logic
from the_tale.linguistics.lexicon import keys
from the_tale.linguistics.lexicon import relations
from the_tale.linguistics.lexicon import exceptions
from the_tale.linguistics.lexicon import dictionary


class LexiconLogicTests(TestCase):

    def setUp(self):
        super(LexiconLogicTests, self).setUp()

    def test_get_verificators_groups__first_substitution(self):
        groups = logic.get_verificators_groups(key=keys.LEXICON_KEY.HERO_COMMON_JOURNAL_LEVEL_UP, old_groups={})
        self.assertEqual(groups, {'hero': (0, 0), 'level': (1, 0)})

    def test_get_verificators_groups__first_substitution__multiple(self):
        groups = logic.get_verificators_groups(key=keys.LEXICON_KEY.QUEST_SEARCH_SMITH_DIARY_UPGRADE__BUY_AND_CHANGE, old_groups={})
        self.assertEqual(groups,
                         {'artifact': (4, 0),
                          'coins': (1, 0),
                          'hero': (0, 0),
                          'receiver': (0, 1),
                          'receiver_position': (2, 0),
                          'sell_price': (1, 1),
                          'unequipped': (4, 1)} )

    def test_get_verificators_groups__existed_substitutions(self):
        old_groups = {'coins': (1, 1),
                      'hero': (0, 2),
                      'receiver': (0, 0),
                      'unequipped': (4, 3)}
        groups = logic.get_verificators_groups(key=keys.LEXICON_KEY.QUEST_SEARCH_SMITH_DIARY_UPGRADE__BUY_AND_CHANGE, old_groups=old_groups)
        self.assertEqual(groups,
                         {'artifact': (4, 0),
                          'coins': (1, 1),
                          'hero': (0, 2),
                          'receiver': (0, 0),
                          'receiver_position': (2, 0),
                          'sell_price': (1, 0),
                          'unequipped': (4, 3)} )

    @mock.patch('the_tale.linguistics.lexicon.relations.VARIABLE_VERIFICATOR.ITEM.substitutions', relations.VARIABLE_VERIFICATOR.ITEM.substitutions[:1])
    def test_get_verificators_groups__no_free_substitution(self):
        self.assertRaises(exceptions.NoFreeVerificatorSubstitutionError,
                          logic.get_verificators_groups, key=keys.LEXICON_KEY.QUEST_SEARCH_SMITH_DIARY_UPGRADE__BUY_AND_CHANGE, old_groups={})

    def test_all_verificators_substitutions_is_in_lexicon_dictionary(self):

        for verificator in relations.VARIABLE_VERIFICATOR.records:
            word_type = verificator.utg_type
            for words in verificator.substitutions:
                for word in words:
                    self.assertTrue(dictionary.DICTIONARY.is_word_registered(word_type, word[0]))
