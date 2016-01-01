# coding: utf-8
from the_tale.common.utils import testcase

from the_tale.game.logic import create_test_map

from .. import modifiers


class ModifiersTests(testcase.TestCase):

    def setUp(self):
        super(ModifiersTests, self).setUp()
        self.place_1, self.place_2, self.place_3 = create_test_map()

    def test_trade_center(self):
        with self.check_increased(lambda: self.place_1.attrs.sell_price):
            with self.check_increased(lambda: self.place_1.attrs.production):
                 with self.check_increased(lambda: self.place_1.attrs.freedom):
                    with self.check_decreased(lambda: self.place_1.attrs.buy_price):
                        self.place_1.set_modifier(modifiers.CITY_MODIFIERS.TRADE_CENTER)

    def test_craft_center(self):
        with self.check_increased(lambda: self.place_1.attrs.buy_artifact_power):
            with self.check_increased(lambda: self.place_1.attrs.production):
                self.place_1.set_modifier(modifiers.CITY_MODIFIERS.CRAFT_CENTER)

    def test_fort(self):
        with self.check_increased(lambda: self.place_1.attrs.safety):
            self.place_1.set_modifier(modifiers.CITY_MODIFIERS.FORT)

    def test_political_center(self):
        with self.check_increased(lambda: self.place_1.attrs.freedom):
            with self.check_increased(lambda: self.place_1.attrs.politic_radius_modifier):
                with self.check_increased(lambda: self.place_1.attrs.stability_renewing_speed):
                    self.place_1.set_modifier(modifiers.CITY_MODIFIERS.POLITICAL_CENTER)

    def test_polic(self):
        with self.check_increased(lambda: self.place_1.attrs.economic):
            with self.check_increased(lambda: self.place_1.attrs.terrain_radius_modifier):
                with self.check_increased(lambda: self.place_1.attrs.freedom):
                    self.place_1.set_modifier(modifiers.CITY_MODIFIERS.POLIC)

    def test_resort(self):
        with self.check_increased(lambda: self.place_1.attrs.hero_regen_chance):
            with self.check_increased(lambda: self.place_1.attrs.companion_regen_chance):
                with self.check_increased(lambda: self.place_1.attrs.safety):
                    with self.check_increased(lambda: self.place_1.attrs.freedom):
                        self.place_1.set_modifier(modifiers.CITY_MODIFIERS.RESORT)

    def test_transport_node(self):
        with self.check_increased(lambda: self.place_1.attrs.transport):
            self.place_1.set_modifier(modifiers.CITY_MODIFIERS.TRANSPORT_NODE)

    def test_outlaws(self):
        with self.check_increased(lambda: self.place_1.attrs.freedom):
            with self.check_decreased(lambda: self.place_1.attrs.safety):
                with self.check_increased(lambda: self.place_1.attrs.experience):
                    self.place_1.set_modifier(modifiers.CITY_MODIFIERS.OUTLAWS)

    def test_holy_city(self):
        with self.check_increased(lambda: self.place_1.attrs.energy_regen_chance):
            with self.check_decreased(lambda: self.place_1.attrs.production):
                with self.check_increased(lambda: self.place_1.attrs.transport):
                    with self.check_decreased(lambda: self.place_1.attrs.freedom):
                        self.place_1.set_modifier(modifiers.CITY_MODIFIERS.HOLY_CITY)
