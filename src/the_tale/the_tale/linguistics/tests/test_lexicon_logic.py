import smart_imports

smart_imports.all()


class LexiconLogicTests(utils_testcase.TestCase):

    def setUp(self):
        super(LexiconLogicTests, self).setUp()

    def test_get_verificators_groups__first_substitution(self):
        groups = lexicon_logic.get_verificators_groups(key=lexicon_keys.LEXICON_KEY.HERO_COMMON_JOURNAL_LEVEL_UP, old_groups={})
        self.assertEqual(groups, {'date': (8, 0), 'time': (9, 0), 'hero': (0, 0), 'hero.weapon': (4, 0), 'level': (1, 0)})

    def test_get_verificators_groups__first_substitution__multiple(self):
        groups = lexicon_logic.get_verificators_groups(key=lexicon_keys.LEXICON_KEY.QUEST_SEARCH_SMITH_DIARY_UPGRADE__BUY_AND_CHANGE, old_groups={})
        self.assertEqual(groups,
                         {'date': (8, 0),
                          'time': (9, 0),
                          'artifact': (4, 0),
                          'coins': (10, 0),
                          'hero': (0, 0),
                          'hero.weapon': (4, 1),
                          'receiver': (0, 1),
                          'receiver_position': (2, 0),
                          'sell_price': (10, 1),
                          'unequipped': (4, 2)})

    def test_get_verificators_groups__existed_substitutions(self):
        old_groups = {'coins': (1, 1),
                      'hero': (0, 2),
                      'receiver': (0, 0),
                      'unequipped': (4, 3)}
        groups = lexicon_logic.get_verificators_groups(key=lexicon_keys.LEXICON_KEY.QUEST_SEARCH_SMITH_DIARY_UPGRADE__BUY_AND_CHANGE, old_groups=old_groups)
        self.assertEqual(groups,
                         {'date': (8, 0),
                          'time': (9, 0),
                          'artifact': (4, 0),
                          'coins': (1, 1),
                          'hero': (0, 2),
                          'hero.weapon': (4, 1),
                          'receiver': (0, 0),
                          'receiver_position': (2, 0),
                          'sell_price': (10, 0),
                          'unequipped': (4, 3)})

    @mock.patch('the_tale.linguistics.lexicon.relations.VARIABLE_VERIFICATOR.ITEM.substitutions', lexicon_relations.VARIABLE_VERIFICATOR.ITEM.substitutions[:1])
    def test_get_verificators_groups__no_free_substitution(self):
        self.assertRaises(lexicon_exceptions.NoFreeVerificatorSubstitutionError,
                          lexicon_logic.get_verificators_groups, key=lexicon_keys.LEXICON_KEY.QUEST_SEARCH_SMITH_DIARY_UPGRADE__BUY_AND_CHANGE, old_groups={})

    def test_all_verificators_substitutions_is_in_lexicon_dictionary(self):

        for verificator in lexicon_relations.VARIABLE_VERIFICATOR.records:
            for words in verificator.substitutions:
                for word in words:
                    if isinstance(word[0], numbers.Number):
                        continue

                    self.assertTrue(lexicon_dictionary.DICTIONARY.has_word(word[0]))
                    self.assertEqual(verificator.utg_type, lexicon_dictionary.DICTIONARY.get_word(word[0]).word.type)

    # during some bug on linguistic migration all old key values was multiplier by 2
    # so, we must folow that practice for new lexicon_keys or change it (it longer )
    # that test check if we follow that practice
    def test_lexicon_keys_values(self):
        for key in lexicon_keys.LEXICON_KEY.records:
            self.assertEqual(key.value // 10000, key.group.index_group // 10000 * 2)

    def test_all_lexicon_keys_variables_in_groups(self):
        for key in lexicon_keys.LEXICON_KEY.records:
            for variable in key.variables:
                self.assertIn(variable, key.group.variables)

    def test_construct_coins(self):
        logic.sync_static_restrictions()

        def expected(value, *records):
            return (utg_constructors.construct_integer(value),
                    [restrictions.get(record) for record in records])

        def check(coins, expected_records):
            value, records = lexicon_relations._construct_coins(coins)

            self.assertEqual(value, utg_constructors.construct_integer(coins))

            self.assertCountEqual(records, [restrictions.get(record) for record in expected_records])

        check(0, [game_relations.COINS_AMOUNT.NO_MONEY,
                  game_relations.COINS_AMOUNT.MAX_COPPER_10,
                  game_relations.COINS_AMOUNT.MAX_SILVER_1,
                  game_relations.COINS_AMOUNT.MAX_SILVER_10,
                  game_relations.COINS_AMOUNT.MAX_GOLD_1,
                  game_relations.COINS_AMOUNT.MAX_GOLD_10,
                  game_relations.COINS_AMOUNT.MAX_GOLD_100,
                  game_relations.COINS_AMOUNT.MAX_GOLD_1000,
                  game_relations.COINS_AMOUNT.BETWEEN_0_10])

        check(100, [game_relations.COINS_AMOUNT.MIN_COPPER_1,
                    game_relations.COINS_AMOUNT.MIN_COPPER_10,
                    game_relations.COINS_AMOUNT.MIN_SILVER_1,
                    game_relations.COINS_AMOUNT.MAX_SILVER_10,
                    game_relations.COINS_AMOUNT.MAX_GOLD_1,
                    game_relations.COINS_AMOUNT.MAX_GOLD_10,
                    game_relations.COINS_AMOUNT.MAX_GOLD_100,
                    game_relations.COINS_AMOUNT.MAX_GOLD_1000,
                    game_relations.COINS_AMOUNT.BETWEEN_100_1000])

        check(10000000, [game_relations.COINS_AMOUNT.MIN_COPPER_1,
                         game_relations.COINS_AMOUNT.MIN_COPPER_10,
                         game_relations.COINS_AMOUNT.MIN_SILVER_1,
                         game_relations.COINS_AMOUNT.MIN_SILVER_10,
                         game_relations.COINS_AMOUNT.MIN_GOLD_1,
                         game_relations.COINS_AMOUNT.MIN_GOLD_10,
                         game_relations.COINS_AMOUNT.MIN_GOLD_100,
                         game_relations.COINS_AMOUNT.MIN_GOLD_1000])
