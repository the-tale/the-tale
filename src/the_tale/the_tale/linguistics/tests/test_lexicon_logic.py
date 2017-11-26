import numbers

from unittest import mock

from utg import constructors as utg_constructors

from the_tale.common.utils.testcase import TestCase

from the_tale.game import relations as game_relations

from .. import storage
from .. import logic as linguistics_logic
from .. import relations as linguistics_relations

from ..lexicon import logic
from ..lexicon import keys
from ..lexicon import relations
from ..lexicon import exceptions
from ..lexicon import dictionary


class LexiconLogicTests(TestCase):

    def setUp(self):
        super(LexiconLogicTests, self).setUp()

    def test_get_verificators_groups__first_substitution(self):
        groups = logic.get_verificators_groups(key=keys.LEXICON_KEY.HERO_COMMON_JOURNAL_LEVEL_UP, old_groups={})
        self.assertEqual(groups, {'date': (8, 0), 'time': (9, 0), 'hero': (0, 0), 'level': (1, 0)})

    def test_get_verificators_groups__first_substitution__multiple(self):
        groups = logic.get_verificators_groups(key=keys.LEXICON_KEY.QUEST_SEARCH_SMITH_DIARY_UPGRADE__BUY_AND_CHANGE, old_groups={})
        self.assertEqual(groups,
                         {'date': (8, 0),
                          'time': (9, 0),
                          'artifact': (4, 0),
                          'coins': (10, 0),
                          'hero': (0, 0),
                          'receiver': (0, 1),
                          'receiver_position': (2, 0),
                          'sell_price': (10, 1),
                          'unequipped': (4, 1)})

    def test_get_verificators_groups__existed_substitutions(self):
        old_groups = {'coins': (1, 1),
                      'hero': (0, 2),
                      'receiver': (0, 0),
                      'unequipped': (4, 3)}
        groups = logic.get_verificators_groups(key=keys.LEXICON_KEY.QUEST_SEARCH_SMITH_DIARY_UPGRADE__BUY_AND_CHANGE, old_groups=old_groups)
        self.assertEqual(groups,
                         {'date': (8, 0),
                          'time': (9, 0),
                          'artifact': (4, 0),
                          'coins': (1, 1),
                          'hero': (0, 2),
                          'receiver': (0, 0),
                          'receiver_position': (2, 0),
                          'sell_price': (10, 0),
                          'unequipped': (4, 3)})

    @mock.patch('the_tale.linguistics.lexicon.relations.VARIABLE_VERIFICATOR.ITEM.substitutions', relations.VARIABLE_VERIFICATOR.ITEM.substitutions[:1])
    def test_get_verificators_groups__no_free_substitution(self):
        self.assertRaises(exceptions.NoFreeVerificatorSubstitutionError,
                          logic.get_verificators_groups, key=keys.LEXICON_KEY.QUEST_SEARCH_SMITH_DIARY_UPGRADE__BUY_AND_CHANGE, old_groups={})

    def test_all_verificators_substitutions_is_in_lexicon_dictionary(self):

        for verificator in relations.VARIABLE_VERIFICATOR.records:
            for words in verificator.substitutions:
                for word in words:
                    if isinstance(word[0], numbers.Number):
                        continue

                    self.assertTrue(dictionary.DICTIONARY.has_word(word[0]))
                    self.assertEqual(verificator.utg_type, dictionary.DICTIONARY.get_word(word[0]).word.type)

    # during some bug on linguistic migration all old key values was multiplier by 2
    # so, we must folow that practice for new keys or change it (it longer )
    # that test check if we follow that practice
    def test_keys_values(self):
        for key in keys.LEXICON_KEY.records:
            self.assertEqual(key.value // 10000, key.group.index_group // 10000 * 2)

    def test_all_keys_variables_in_groups(self):
        for key in keys.LEXICON_KEY.records:
            for variable in key.variables:
                self.assertIn(variable, key.group.variables)

    def test_construct_coins(self):
        linguistics_logic.sync_static_restrictions()

        def expected(value, record):
            return (utg_constructors.construct_integer(value),
                    [storage.restrictions_storage.get_restriction(linguistics_relations.TEMPLATE_RESTRICTION_GROUP.COINS_AMOUNT,
                                                                  record.value).id])

        self.assertEqual(relations._construct_coins(0), expected(0, game_relations.COINS_AMOUNT.NO_MONEY))
        self.assertEqual(relations._construct_coins(100), expected(100, game_relations.COINS_AMOUNT.SILVER_1))
        self.assertEqual(relations._construct_coins(10000000), expected(10000000, game_relations.COINS_AMOUNT.GOLD_1000))
