# coding: utf-8
from the_tale.common.utils import testcase

from the_tale.game.logic import create_test_map

from the_tale.game.persons.relations import PERSON_TYPE

from the_tale.game.map.places.modifiers import MODIFIERS
from the_tale.game.map.places.modifiers.prototypes import TradeCenter, CraftCenter, Fort, PoliticalCenter, Polic, Resort, TransportNode, Outlaws
from the_tale.game.map.places.conf import places_settings

class ModifiersTests(testcase.TestCase):

    def setUp(self):
        super(ModifiersTests, self).setUp()
        self.place_1, self.place_2, self.place_3 = create_test_map()

    def test_all_professions_covered(self):
        for modifier_class in MODIFIERS.values():
            modifier = modifier_class(place=self.place_1)
            for person_type in PERSON_TYPE.records:
                self.assertTrue(person_type.value in modifier.PERSON_EFFECTS)

    def test_trade_center(self):
        self.assertEqual(CraftCenter(self.place_1).modify_sell_price(100), 100)
        self.assertEqual(CraftCenter(self.place_1).modify_buy_price(100), 100)
        self.assertTrue(TradeCenter(self.place_1).modify_sell_price(100) > 100)
        self.assertTrue(TradeCenter(self.place_1).modify_buy_price(100) < 100)

    def test_craft_center(self):
        self.assertEqual(sum(TradeCenter(self.place_1).modify_buy_better_artifact(1) for i in xrange(100)), 100)
        self.assertTrue(sum(CraftCenter(self.place_1).modify_buy_better_artifact(1) for i in xrange(100)) > 100)

    def test_fort(self):
        self.assertEqual(Fort.SAFETY_MODIFIER, 0.05)

    def test_political_center(self):
        self.assertEqual(PoliticalCenter.FREEDOM_MODIFIER, 0.25)
        self.assertEqual(PoliticalCenter(self.place_1).modify_terrain_owning_radius(100), 125)

        old_radius = self.place_1.terrain_owning_radius

        self.place_1.modifier = PoliticalCenter(self.place_1)

        self.assertTrue(old_radius < self.place_1.terrain_owning_radius)

    def test_polic(self):
        self.assertEqual(CraftCenter(self.place_1).modify_economic_size(100), 100)
        self.assertEqual(CraftCenter(self.place_1).modify_terrain_change_power(100), 100)

        self.assertEqual(Polic(self.place_1).modify_economic_size(places_settings.MAX_SIZE+2), places_settings.MAX_SIZE+3)
        self.assertEqual(Polic(self.place_1).modify_economic_size(1), 2)
        self.assertEqual(Polic(self.place_1).modify_terrain_change_power(100), 120)

    def test_resort(self):
        self.assertFalse(CraftCenter(self.place_1).full_regen_allowed())
        self.assertTrue(Resort(self.place_1).full_regen_allowed())

    def test_transport_node(self):
        self.assertEqual(TransportNode.TRANSPORT_MODIFIER, 0.2)

    def test_outlaws(self):
        self.assertEqual(Outlaws.FREEDOM_MODIFIER, 0.35)
        self.assertEqual(Outlaws.SAFETY_MODIFIER, -0.1)
        self.assertEqual(Outlaws.EXPERIENCE_MODIFIER, 0.25)
