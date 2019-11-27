
import smart_imports

smart_imports.all()


class CreateCardTest(utils_testcase.TestCase):

    def setUp(self):
        super().setUp()
        game_logic.create_test_map()

    def test_single_card(self):
        card = logic.create_card(allow_premium_cards=False)
        self.assertTrue(card.uid)

    def test_simple(self):

        created_cards = set()
        rarities = set()

        companions_models.CompanionRecord.objects.all().delete()
        companions_storage.companions.refresh()

        for rarity, rarity_abilities in companions_helpers.RARITIES_ABILITIES.items():
            companions_logic.create_random_companion_record('%s companion' % rarity,
                                                            mode=companions_relations.MODE.AUTOMATIC,
                                                            abilities=rarity_abilities,
                                                            state=companions_relations.STATE.ENABLED)

        for i in range(len(types.CARD.records) * 10):
            card = logic.create_card(allow_premium_cards=True)
            created_cards.add(card.type)
            rarities.add(card.type.rarity)

        self.assertTrue(len(types.CARD.records) > len(created_cards) / 2)
        self.assertEqual(rarities, set(relations.RARITY.records))

    def test_not_premium(self):
        for i in range(len(types.CARD.records) * 10):
            card = logic.create_card(allow_premium_cards=False)
            self.assertFalse(card.type.availability.is_FOR_PREMIUMS)

    def test_auction_availability_not_specified_not_premium(self):
        self.assertFalse(logic.create_card(allow_premium_cards=True, available_for_auction=False).available_for_auction)
        self.assertTrue(logic.create_card(allow_premium_cards=True, available_for_auction=True).available_for_auction)

    def test_priority(self):
        rarities = collections.Counter(logic.create_card(allow_premium_cards=True).type.rarity
                                       for i in range(len(types.CARD.records) * 100))

        last_rarity_count = 999999999999

        for rarity in relations.RARITY.records:
            self.assertTrue(last_rarity_count >= rarities[rarity])
            last_rarity_count = rarities[rarity]

    def test_rarity(self):
        for rarity in relations.RARITY.records:
            for i in range(100):
                card = logic.create_card(allow_premium_cards=True, rarity=rarity)
                self.assertEqual(card.type.rarity, rarity)

    @mock.patch('the_tale.game.cards.effects.ChangePreference.allowed_preferences', lambda self: [heroes_relations.PREFERENCE_TYPE.records[0]])
    @mock.patch('the_tale.game.cards.effects.ChangeItemOfExpenditure.allowed_items', lambda self: [heroes_relations.ITEMS_OF_EXPENDITURE.records[0]])
    @mock.patch('the_tale.game.cards.effects.ChangeHabit.allowed_habits', lambda self: [game_relations.HABIT_TYPE.records[0]])
    @mock.patch('the_tale.game.cards.effects.ChangeHabit.allowed_directions', lambda self: [1])
    @mock.patch('the_tale.game.cards.effects.AddPersonPower.allowed_directions', lambda self: [1])
    @mock.patch('the_tale.game.cards.effects.AddPlacePower.allowed_directions', lambda self: [1])
    @mock.patch('the_tale.game.cards.effects.EmissaryQuest.allowed_actions', lambda self: [quests_relations.PERSON_ACTION.HARM])
    @mock.patch('the_tale.game.cards.effects.ChangeHistory.allowed_history', lambda self: [effects.ChangeHistory.HISTORY_TYPE.records[0]])
    def test_exclude(self):
        created_cards = []

        companions_models.CompanionRecord.objects.all().delete()
        companions_storage.companions.refresh()

        for rarity, rarity_abilities in companions_helpers.RARITIES_ABILITIES.items():
            companions_logic.create_random_companion_record('%s companion' % rarity,
                                                            mode=companions_relations.MODE.AUTOMATIC,
                                                            abilities=rarity_abilities,
                                                            state=companions_relations.STATE.ENABLED)

        for i in range(len([card_type for card_type in types.CARD.records])):
            card = logic.create_card(allow_premium_cards=True, exclude=created_cards)
            created_cards.append(card)

        self.assertEqual(logic.create_card(allow_premium_cards=True, exclude=created_cards), None)

        self.assertEqual(set(card.type for card in created_cards), set(card_type for card_type in types.CARD.records))

    @mock.patch('the_tale.game.cards.effects.ChangePreference.allowed_preferences', lambda self: [heroes_relations.PREFERENCE_TYPE.records[0]])
    @mock.patch('the_tale.game.cards.effects.ChangeItemOfExpenditure.allowed_items', lambda self: [heroes_relations.ITEMS_OF_EXPENDITURE.records[0]])
    @mock.patch('the_tale.game.cards.effects.ChangeHabit.allowed_habits', lambda self: [game_relations.HABIT_TYPE.records[0]])
    @mock.patch('the_tale.game.cards.effects.ChangeHabit.allowed_directions', lambda self: [1])
    @mock.patch('the_tale.game.cards.effects.AddPersonPower.allowed_directions', lambda self: [1])
    @mock.patch('the_tale.game.cards.effects.AddPlacePower.allowed_directions', lambda self: [1])
    @mock.patch('the_tale.game.cards.effects.EmissaryQuest.allowed_actions', lambda self: [quests_relations.PERSON_ACTION.HARM])
    @mock.patch('the_tale.game.cards.effects.ChangeHistory.allowed_history', lambda self: [effects.ChangeHistory.HISTORY_TYPE.records[0]])
    def test_exclude__different_data(self):
        created_cards = []

        companions_models.CompanionRecord.objects.all().delete()
        companions_storage.companions.refresh()

        for rarity, rarity_abilities in companions_helpers.RARITIES_ABILITIES.items():
            companions_logic.create_random_companion_record('%s companion' % rarity,
                                                            mode=companions_relations.MODE.AUTOMATIC,
                                                            abilities=rarity_abilities,
                                                            state=companions_relations.STATE.ENABLED)

        for i in range(len([card_type for card_type in types.CARD.records])):
            card = logic.create_card(allow_premium_cards=True, exclude=created_cards)
            created_cards.append(card)

        self.assertEqual(logic.create_card(allow_premium_cards=True, exclude=created_cards), None)

        created_cards[0].data = {'fake-data': True}
        self.assertEqual(created_cards[0].type, logic.create_card(allow_premium_cards=True, exclude=created_cards).type)

        self.assertEqual(set(card.type for card in created_cards), set(card_type for card_type in types.CARD.records))


class GetCombinedCardTests(utils_testcase.TestCase):

    def setUp(self):
        super().setUp()
        game_logic.create_test_map()

    def create_card(self, type, available_for_auction=True, uid=None):
        return type.effect.create_card(type=type,
                                       uid=uid,
                                       available_for_auction=available_for_auction)

    def test_no_cards(self):
        cards, result = logic.get_combined_cards(allow_premium_cards=True,
                                                 combined_cards=())
        self.assertEquals(cards, None)
        self.assertTrue(result.is_NO_CARDS)

    def test_equal_rarity_required(self):
        cards, result = logic.get_combined_cards(allow_premium_cards=True,
                                                 combined_cards=(self.create_card(types.CARD.ADD_POWER_COMMON),
                                                                 self.create_card(types.CARD.ADD_POWER_UNCOMMON)))
        self.assertEqual(cards, None)
        self.assertTrue(result.is_EQUAL_RARITY_REQUIRED)

    def test_duplicate_ids(self):
        uid = uuid.uuid4()
        cards, result = logic.get_combined_cards(allow_premium_cards=True,
                                                 combined_cards=(self.create_card(types.CARD.ADD_POWER_COMMON, uid=uid),
                                                                 self.create_card(types.CARD.ADD_POWER_UNCOMMON, uid=uid)))
        self.assertEqual(cards, None)
        self.assertTrue(result.is_EQUAL_RARITY_REQUIRED)

    def test_combine_1_common(self):
        cards, result = logic.get_combined_cards(allow_premium_cards=True,
                                                 combined_cards=(self.create_card(types.CARD.ADD_POWER_COMMON),))
        self.assertEqual(cards, None)
        self.assertTrue(result.is_COMBINE_1_COMMON)

    def test_combine_1(self):
        cards, result = logic.get_combined_cards(allow_premium_cards=True,
                                                 combined_cards=(self.create_card(types.CARD.ADD_POWER_UNCOMMON),))
        self.assertEqual(len(cards), 1)
        self.assertTrue(cards[0].type.rarity.is_COMMON)
        self.assertTrue(result.is_SUCCESS)

    def test_combine_1__multiple_results(self):
        cards, result = logic.get_combined_cards(allow_premium_cards=True,
                                                 combined_cards=(self.create_card(types.CARD.CREATE_CLAN),))
        self.assertEqual(len(cards), 9)
        self.assertTrue(all(card.type.is_EMISSARY_QUEST for card in cards))

        self.assertTrue(cards[0].type.rarity.value < types.CARD.CREATE_CLAN.rarity.value)

        self.assertTrue(result.is_SUCCESS)

    def test_combine_2_reactor(self):
        combined_card_1 = self.create_card(types.CARD.CHANGE_HABIT_EPIC)
        combined_card_2 = self.create_card(types.CARD.CHANGE_HABIT_EPIC)

        cards, result = logic.get_combined_cards(allow_premium_cards=True,
                                                 combined_cards=(combined_card_1, combined_card_2))
        self.assertEqual(len(cards), 1)
        self.assertTrue(result.is_SUCCESS)

        self.assertEqual(cards[0].type, types.CARD.CHANGE_HABIT_EPIC)
        self.assertNotEqual(combined_card_1.data, cards[0].data)
        self.assertNotEqual(combined_card_2.data, cards[0].data)

    def test_combine_2_random(self):
        cards, result = logic.get_combined_cards(allow_premium_cards=True,
                                                 combined_cards=(self.create_card(types.CARD.CHANGE_HABIT_EPIC),
                                                                 self.create_card(types.CARD.ADD_EXPERIENCE_EPIC)))
        self.assertEqual(len(cards), 1)
        self.assertTrue(result.is_SUCCESS)

    def test_get_combined_card_3_reactor(self):
        combined_card_1 = self.create_card(types.CARD.CHANGE_HABIT_EPIC)
        combined_card_2 = self.create_card(types.CARD.CHANGE_HABIT_EPIC)
        combined_card_3 = self.create_card(types.CARD.CHANGE_HABIT_EPIC)

        combined_card_2.data = combined_card_1.data
        combined_card_3.data = combined_card_1.data

        cards, result = logic.get_combined_cards(allow_premium_cards=True,
                                                 combined_cards=(combined_card_1, combined_card_2, combined_card_3))
        self.assertEqual(len(cards), 1)
        self.assertTrue(result.is_SUCCESS)

        self.assertEqual(cards[0].type, types.CARD.CHANGE_HABIT_LEGENDARY)
        self.assertEqual(combined_card_1.data, cards[0].data)

    def test_get_combined_card_3__random(self):
        cards, result = logic.get_combined_cards(allow_premium_cards=True,
                                                 combined_cards=(self.create_card(types.CARD.CHANGE_HABIT_EPIC),
                                                                 self.create_card(types.CARD.CHANGE_HABIT_EPIC),
                                                                 self.create_card(types.CARD.ADD_EXPERIENCE_EPIC)))
        self.assertEqual(len(cards), 1)
        self.assertTrue(cards[0].type.rarity.is_LEGENDARY)
        self.assertTrue(result.is_SUCCESS)

    def test_combine_3_legendary(self):
        cards, result = logic.get_combined_cards(allow_premium_cards=True,
                                                 combined_cards=(self.create_card(types.CARD.CHANGE_HABIT_LEGENDARY),
                                                                 self.create_card(types.CARD.CHANGE_HABIT_LEGENDARY),
                                                                 self.create_card(types.CARD.ADD_EXPERIENCE_LEGENDARY)))
        self.assertEqual(cards, None)
        self.assertTrue(result.is_COMBINE_3_LEGENDARY)

    def test_combine_too_many_cards(self):
        cards, result = logic.get_combined_cards(allow_premium_cards=True,
                                                 combined_cards=(self.create_card(types.CARD.CHANGE_HABIT_EPIC),
                                                                 self.create_card(types.CARD.CHANGE_HABIT_EPIC),
                                                                 self.create_card(types.CARD.CHANGE_HABIT_EPIC),
                                                                 self.create_card(types.CARD.CHANGE_HABIT_EPIC)))
        self.assertEqual(cards, None)
        self.assertTrue(result.is_TOO_MANY_CARDS)

    def test_combine_too_many_cards_allowed(self):
        combined_cards = [self.create_card(types.CARD.EMISSARY_QUEST)
                          for _ in range(9)]

        cards, result = logic.get_combined_cards(allow_premium_cards=True,
                                                 combined_cards=combined_cards)
        self.assertEqual(len(cards), 1)
        self.assertTrue(cards[0].type.is_CREATE_CLAN)

    def test_allow_premium_cards__allowed(self):
        availability = set()

        for i in range(1000):
            cards, result = logic.get_combined_cards(allow_premium_cards=True,
                                                     combined_cards=(self.create_card(types.CARD.CHANGE_HABIT_EPIC),
                                                                     self.create_card(types.CARD.CHANGE_HABIT_EPIC),
                                                                     self.create_card(types.CARD.ADD_EXPERIENCE_EPIC)))
            self.assertEqual(len(cards), 1)
            availability.add(cards[0].type.availability)

        self.assertEqual(availability, set(relations.AVAILABILITY.records))

    def test_allow_premium_cards__not_allowed(self):
        availability = set()

        for i in range(1000):
            cards, result = logic.get_combined_cards(allow_premium_cards=False,
                                                     combined_cards=(self.create_card(types.CARD.CHANGE_HABIT_EPIC),
                                                                     self.create_card(types.CARD.CHANGE_HABIT_EPIC),
                                                                     self.create_card(types.CARD.ADD_EXPERIENCE_EPIC)))
            self.assertEqual(len(cards), 1)
            availability.add(cards[0].type.availability)

        self.assertEqual(availability, {relations.AVAILABILITY.FOR_ALL})

    def test_available_for_auction__available(self):
        cards, result = logic.get_combined_cards(allow_premium_cards=True,
                                                 combined_cards=(self.create_card(types.CARD.CHANGE_HABIT_EPIC),
                                                                 self.create_card(types.CARD.CHANGE_HABIT_EPIC),
                                                                 self.create_card(types.CARD.ADD_EXPERIENCE_EPIC)))
        self.assertEqual(len(cards), 1)
        self.assertTrue(cards[0].available_for_auction)

    def test_available_for_auction__not_available(self):
        cards, result = logic.get_combined_cards(allow_premium_cards=True,
                                                 combined_cards=(self.create_card(types.CARD.CHANGE_HABIT_EPIC),
                                                                 self.create_card(types.CARD.CHANGE_HABIT_EPIC,
                                                                                  available_for_auction=False),
                                                                 self.create_card(types.CARD.ADD_EXPERIENCE_EPIC)))
        self.assertEqual(len(cards), 1)
        self.assertFalse(cards[0].available_for_auction)


class StorageOperationsTest(utils_testcase.TestCase):

    def setUp(self):
        super().setUp()
        game_logic.create_test_map()

        tt_services.storage.cmd_debug_clear_service()

        companions_models.CompanionRecord.objects.all().delete()
        companions_storage.companions.refresh()

        for rarity, rarity_abilities in companions_helpers.RARITIES_ABILITIES.items():
            companions_logic.create_random_companion_record('%s companion' % rarity,
                                                            mode=companions_relations.MODE.AUTOMATIC,
                                                            abilities=rarity_abilities,
                                                            state=companions_relations.STATE.ENABLED)

        self.cards = [objects.Card(types.CARD.KEEPERS_GOODS_COMMON, uid=uuid.uuid4()),
                      objects.Card(types.CARD.ADD_GOLD_COMMON, uid=uuid.uuid4()),
                      objects.Card(types.CARD.KEEPERS_GOODS_LEGENDARY, uid=uuid.uuid4()),
                      types.CARD.GET_COMPANION_UNCOMMON.effect.create_card(types.CARD.GET_COMPANION_UNCOMMON, available_for_auction=True),
                      objects.Card(types.CARD.KEEPERS_GOODS_COMMON, uid=uuid.uuid4()),
                      objects.Card(types.CARD.ADD_GOLD_COMMON, uid=uuid.uuid4())]

    def fill_storage(self):
        logic.change_cards(owner_id=666,
                           operation_type='#test',
                           to_add=[self.cards[0], self.cards[1], self.cards[3]],
                           to_remove=[])

        logic.change_cards(owner_id=777,
                           operation_type='#test',
                           to_add=[self.cards[4]],
                           to_remove=[])

        logic.change_cards(owner_id=666,
                           operation_type='#test',
                           to_add=[self.cards[2], self.cards[5]],
                           to_remove=[self.cards[1]])

    def test_load_no_cards(self):
        cards = tt_services.storage.cmd_get_items(666)
        self.assertEqual(cards, {})

    def test_change_and_load(self):
        self.fill_storage()
        cards = tt_services.storage.cmd_get_items(666)

        self.assertEqual(cards, {card.uid: card for card in [self.cards[0], self.cards[2], self.cards[3], self.cards[5]]})

    def test_has_card(self):
        self.fill_storage()

        self.assertTrue(logic.has_cards(666, [self.cards[0].uid, self.cards[3].uid]))
        self.assertFalse(logic.has_cards(666, [self.cards[0].uid, self.cards[4].uid]))

    def test_change_cards_owner(self):

        logic.change_cards(owner_id=666,
                           operation_type='#test',
                           to_add=[self.cards[0], self.cards[1], self.cards[3]],
                           to_remove=[])

        logic.change_owner(old_owner_id=666,
                           new_owner_id=888,
                           operation_type='#test-move',
                           new_storage=relations.STORAGE.FAST,
                           cards_ids=[self.cards[0].uid, self.cards[3].uid])

        self.assertTrue(logic.has_cards(666, [self.cards[1].uid]))
        self.assertFalse(logic.has_cards(666, [self.cards[0].uid, self.cards[3].uid]))

        self.assertFalse(logic.has_cards(888, [self.cards[1].uid]))
        self.assertTrue(logic.has_cards(888, [self.cards[0].uid, self.cards[3].uid]))
