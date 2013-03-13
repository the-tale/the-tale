# coding: utf-8
from common.utils import testcase

from game.logic import create_test_map

from game.persons.relations import PERSON_TYPE

from game.map.places.modifiers import MODIFIERS
from game.map.places.modifiers.prototypes import TradeCenter, CraftCenter, Fort, PoliticalCenter, Polic, Resort, TransportNode
from game.map.places.conf import places_settings

class ModifiersTests(testcase.TestCase):

    def setUp(self):
        super(ModifiersTests, self).setUp()
        self.place_1, self.place_2, self.place_3 = create_test_map()

    def test_all_professions_covered(self):
        for modifier in MODIFIERS.values():
            for person_type in PERSON_TYPE._records:
                self.assertTrue(person_type.value in modifier.PERSON_EFFECTS)

    def test_trade_center(self):
        self.assertEqual(CraftCenter(self.place_1).modify_sell_price(100), 100)
        self.assertEqual(CraftCenter(self.place_1).modify_buy_price(100), 100)
        self.assertTrue(TradeCenter(self.place_1).modify_sell_price(100) > 100)
        self.assertTrue(TradeCenter(self.place_1).modify_buy_price(100) < 100)

    def test_craft_center(self):
        self.assertFalse(any(TradeCenter(self.place_1).can_buy_better_artifact() for i in xrange(100)))
        self.assertTrue(any(CraftCenter(self.place_1).can_buy_better_artifact() for i in xrange(100)))

    def test_fort(self):
        self.assertEqual(CraftCenter(self.place_1).modify_battles_per_turn(100), 100)
        self.assertTrue(Fort(self.place_1).modify_battles_per_turn(0.2) < 0.2)

    def test_political_center(self):
        self.assertEqual(Fort(self.place_1).modify_power(100), 100)
        self.assertTrue(PoliticalCenter(self.place_1).modify_power(100) > 100)
        self.assertTrue(PoliticalCenter(self.place_1).modify_power(-100) < -100)

    def test_polic(self):
        self.assertEqual(CraftCenter(self.place_1).modify_place_size(100), 100)
        self.assertEqual(CraftCenter(self.place_1).modify_terrain_change_power(100), 100)

        self.assertEqual(Polic(self.place_1).modify_place_size(places_settings.MAX_SIZE+2), places_settings.MAX_SIZE)
        self.assertTrue(Polic(self.place_1).modify_place_size(1) > 1)
        self.assertTrue(Polic(self.place_1).modify_terrain_change_power(100) > 100)

    def test_resort(self):
        self.assertFalse(CraftCenter(self.place_1).full_regen_allowed())
        self.assertTrue(Resort(self.place_1).full_regen_allowed())

    def test_transport_node(self):
        self.assertEqual(CraftCenter(self.place_1).modify_move_speed(100), 100)
        self.assertTrue(TransportNode(self.place_1).modify_move_speed(100) > 100)
