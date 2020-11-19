
import smart_imports

smart_imports.all()


class ModifiersTests(utils_testcase.TestCase):

    def setUp(self):
        super(ModifiersTests, self).setUp()
        self.place_1, self.place_2, self.place_3 = game_logic.create_test_map()

        self.place_1.attrs.size = 5
        self.place_1.refresh_attributes()

    @mock.patch('the_tale.game.places.objects.Place.is_modifier_active', lambda self: True)
    def test_trade_center(self):
        with self.check_increased(lambda: self.place_1.attrs.sell_price):
            with self.check_increased(lambda: self.place_1.attrs.freedom):
                with self.check_increased(lambda: self.place_1.attrs.culture):
                    with self.check_decreased(lambda: self.place_1.attrs.buy_price):
                        self.place_1.set_modifier(modifiers.CITY_MODIFIERS.TRADE_CENTER)

    @mock.patch('the_tale.game.places.objects.Place.is_modifier_active', lambda self: True)
    def test_craft_center(self):
        with self.check_increased(lambda: self.place_1.attrs.production):
            self.place_1.set_modifier(modifiers.CITY_MODIFIERS.CRAFT_CENTER)

    @mock.patch('the_tale.game.balance.constants.PLACE_STABILITY_PENALTY_FOR_SPECIALIZATION', -100500)
    @mock.patch('the_tale.game.balance.constants.PLACE_TYPE_ENOUGH_BORDER', 100)
    @mock.patch('the_tale.game.places.objects.Place.is_modifier_active', lambda self: False)
    def test_craft_center__modifier_disabled(self):
        with self.check_decreased(lambda: self.place_1.attrs.stability):
            self.place_1.set_modifier(modifiers.CITY_MODIFIERS.CRAFT_CENTER)

    @mock.patch('the_tale.game.places.objects.Place.is_modifier_active', lambda self: True)
    def test_fort(self):
        with self.check_increased(lambda: self.place_1.attrs.safety):
            self.place_1.set_modifier(modifiers.CITY_MODIFIERS.FORT)

    @mock.patch('the_tale.game.places.objects.Place.is_modifier_active', lambda self: True)
    def test_political_center(self):
        logic.register_effect(place_id=self.place_1.id,
                              attribute=relations.ATTRIBUTE.STABILITY,
                              value=-1,
                              name='test',
                              refresh_effects=True,
                              refresh_places=True)

        with self.check_increased(lambda: self.place_1.attrs.freedom):
            with self.check_increased(lambda: self.place_1.attrs.politic_radius):
                with self.check_increased(lambda: self.place_1.attrs.stability):
                    self.place_1.set_modifier(modifiers.CITY_MODIFIERS.POLITICAL_CENTER)

    @mock.patch('the_tale.game.places.objects.Place.is_modifier_active', lambda self: True)
    def test_polic(self):
        with self.check_increased(lambda: self.place_1.attrs.culture):
            with self.check_increased(lambda: self.place_1.attrs.freedom):
                self.place_1.set_modifier(modifiers.CITY_MODIFIERS.POLIC)

    @mock.patch('the_tale.game.places.objects.Place.is_modifier_active', lambda self: True)
    def test_resort(self):
        with self.check_increased(lambda: self.place_1.attrs.hero_regen_chance):
            with self.check_increased(lambda: self.place_1.attrs.companion_regen_chance):
                with self.check_increased(lambda: self.place_1.attrs.safety):
                    with self.check_increased(lambda: self.place_1.attrs.freedom):
                        self.place_1.set_modifier(modifiers.CITY_MODIFIERS.RESORT)

    @mock.patch('the_tale.game.places.objects.Place.is_modifier_active', lambda self: True)
    def test_transport_node(self):
        self.place_1.refresh_attributes()

        with self.check_increased(lambda: self.place_1.attrs.transport):
            self.place_1.set_modifier(modifiers.CITY_MODIFIERS.TRANSPORT_NODE)

    @mock.patch('the_tale.game.places.objects.Place.is_modifier_active', lambda self: True)
    def test_outlaws(self):
        self.place_1.refresh_attributes()

        with self.check_increased(lambda: self.place_1.attrs.freedom):
            with self.check_decreased(lambda: self.place_1.attrs.safety):
                with self.check_increased(lambda: self.place_1.attrs.experience_bonus):
                    self.place_1.set_modifier(modifiers.CITY_MODIFIERS.OUTLAWS)

    @mock.patch('the_tale.game.places.objects.Place.is_modifier_active', lambda self: True)
    def test_holy_city(self):
        # size must not be equal 1, becouse in that case production below zero will be compenstated with tax
        self.place_1.attrs.size = 10
        self.place_1.refresh_attributes()

        with self.check_increased(lambda: self.place_1.attrs.reset_religion_ceremony_timeout_chance):
            with self.check_decreased(lambda: self.place_1.attrs.production):
                with self.check_increased(lambda: self.place_1.attrs.transport):
                    with self.check_decreased(lambda: self.place_1.attrs.freedom):
                        self.place_1.set_modifier(modifiers.CITY_MODIFIERS.HOLY_CITY)
