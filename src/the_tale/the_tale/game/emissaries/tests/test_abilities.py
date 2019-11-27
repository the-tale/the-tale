
import smart_imports

smart_imports.all()


class AbilitiesTests(utils_testcase.TestCase):

    def setUp(self):
        super().setUp()
        self.abilities = abilities.Abilities()

    def test_initialization(self):
        self.assertEqual(self.abilities._abilities, {})

    def test_dict_operations(self):
        self.abilities[relations.ABILITY.ECONOMY] = 1
        self.abilities[relations.ABILITY.TECHNOLOGIES] = -10

        self.abilities[relations.ABILITY.SOCIOLOGY] -= 5
        self.abilities[relations.ABILITY.SOCIOLOGY] += 33

        self.assertEqual(self.abilities[relations.ABILITY.ECONOMY], 1)
        self.assertEqual(self.abilities[relations.ABILITY.TECHNOLOGIES], -10)
        self.assertEqual(self.abilities[relations.ABILITY.SOCIOLOGY], 28)

        self.assertEqual(self.abilities[relations.ABILITY.POLITICAL_SCIENCE], 0)

        with self.assertRaises(KeyError):
            self.abilities['wrong ability']

    def test_items(self):
        self.assertEqual({key: value for key, value in self.abilities.items()},
                         {ability: 0 for ability in relations.ABILITY.records})

        test_ability = relations.ABILITY.random()

        self.abilities[test_ability] = 666

        self.assertEqual({key: value for key, value in self.abilities.items()},
                         {ability: (0 if ability != test_ability else 666) for ability in relations.ABILITY.records})

    def test_serialization(self):
        test_ability = relations.ABILITY.random()

        self.abilities[test_ability] = 666

        self.assertEqual(self.abilities, abilities.Abilities.deserialize(self.abilities.serialize()))

    def test_total_level(self):
        self.abilities[relations.ABILITY.ECONOMY] = 1
        self.abilities[relations.ABILITY.TECHNOLOGIES] = -10

        self.abilities[relations.ABILITY.SOCIOLOGY] -= 5
        self.abilities[relations.ABILITY.SOCIOLOGY] += 33

        self.assertEqual(self.abilities.total_level(), 1 - 10 - 5 + 33)


class AbilitiesGrowTests(utils_testcase.TestCase,
                         clans_helpers.ClansTestsMixin,
                         helpers.EmissariesTestsMixin):

    def setUp(self):
        super().setUp()

        self.places = game_logic.create_test_map()

        clans_tt_services.chronicle.cmd_debug_clear_service()

        self.forum_category = forum_prototypes.CategoryPrototype.create(caption='category-1',
                                                                        slug=clans_conf.settings.FORUM_CATEGORY_SLUG,
                                                                        order=0)

        self.account = self.accounts_factory.create_account()
        self.clan = self.create_clan(owner=self.account, uid=1)

        self.emissary = self.create_emissary(clan=self.clan,
                                             initiator=self.account,
                                             place_id=random.choice(self.places).id)

    def test_grow(self):

        self.emissary.attrs.attribute_grow_speed__economy = 20
        self.emissary.attrs.attribute_grow_speed__sociology = 1

        self.emissary.abilities.grow(self.emissary.attrs, [relations.ABILITY.ECONOMY,
                                                           relations.ABILITY.CULTURAL_SCIENCE])
        self.emissary.abilities.grow(self.emissary.attrs, [relations.ABILITY.TECHNOLOGIES,
                                                           relations.ABILITY.SOCIOLOGY,
                                                           relations.ABILITY.ECONOMY])

        expected_values = {ability: 0 for ability in relations.ABILITY.records}
        expected_values[relations.ABILITY.ECONOMY] = 40
        expected_values[relations.ABILITY.SOCIOLOGY] = 1
        expected_values[relations.ABILITY.TECHNOLOGIES] = self.emissary.attrs.attribute_grow_speed__technologies
        expected_values[relations.ABILITY.CULTURAL_SCIENCE] = self.emissary.attrs.attribute_grow_speed__cultural_science

        self.assertEqual(dict(self.emissary.abilities.items()), expected_values)

    def test_grow__maximum(self):
        self.emissary.attrs.attribute_grow_speed__economy = 10005000

        self.emissary.abilities.grow(self.emissary.attrs, [relations.ABILITY.ECONOMY,
                                                           relations.ABILITY.CULTURAL_SCIENCE])
        self.emissary.abilities.grow(self.emissary.attrs, [relations.ABILITY.TECHNOLOGIES,
                                                           relations.ABILITY.SOCIOLOGY,
                                                           relations.ABILITY.ECONOMY])

        self.assertEqual(self.emissary.abilities[relations.ABILITY.ECONOMY], self.emissary.attrs.attribute_maximum__economy)
