
import smart_imports

smart_imports.all()


class PersonTests(utils_testcase.TestCase):

    def setUp(self):
        super(PersonTests, self).setUp()
        game_turn.increment()

        self.persons_changed_at_turn = game_turn.number()

        self.p1, self.p2, self.p3 = game_logic.create_test_map()

        self.person = helpers.create_person(self.p1)

        account = self.accounts_factory.create_account()
        self.hero_1 = heroes_logic.load_hero(account_id=account.id)

        account = self.accounts_factory.create_account()
        self.hero_2 = heroes_logic.load_hero(account_id=account.id)

        account = self.accounts_factory.create_account()
        self.hero_3 = heroes_logic.load_hero(account_id=account.id)

        game_turn.increment()

    def test_initialize(self):
        self.assertEqual(self.person.place.persons_changed_at_turn, self.persons_changed_at_turn)

        self.assertEqual(self.person.created_at_turn, game_turn.number() - 1)

    def test_place_effects__economic_and_specialization(self):
        self.person.personality_cosmetic = relations.PERSONALITY_COSMETIC.TRUTH_SEEKER
        self.person.personality_practical = relations.PERSONALITY_PRACTICAL.MULTIWISE
        self.person.refresh_attributes()

        place_attributes = set(effect.attribute for effect in self.person.place_effects())

        self.assertEqual(place_attributes,
                         set((places_relations.ATTRIBUTE.PRODUCTION,
                              places_relations.ATTRIBUTE.SAFETY,
                              places_relations.ATTRIBUTE.TRANSPORT,
                              places_relations.ATTRIBUTE.FREEDOM,
                              places_relations.ATTRIBUTE.STABILITY,
                              places_relations.ATTRIBUTE.CULTURE,

                              places_relations.ATTRIBUTE.MODIFIER_TRANSPORT_NODE,
                              places_relations.ATTRIBUTE.MODIFIER_OUTLAWS,
                              places_relations.ATTRIBUTE.MODIFIER_HOLY_CITY,
                              places_relations.ATTRIBUTE.MODIFIER_CRAFT_CENTER,
                              places_relations.ATTRIBUTE.MODIFIER_FORT,
                              places_relations.ATTRIBUTE.MODIFIER_POLITICAL_CENTER,
                              places_relations.ATTRIBUTE.MODIFIER_TRADE_CENTER,
                              places_relations.ATTRIBUTE.MODIFIER_POLIC,
                              places_relations.ATTRIBUTE.MODIFIER_RESORT)))

    def test_place_effects__terrain_radius_bonus(self):
        self.person.personality_cosmetic = relations.PERSONALITY_COSMETIC.FIDGET
        self.person.personality_practical = relations.PERSONALITY_PRACTICAL.MULTIWISE
        self.person.refresh_attributes()

        place_attributes = set(effect.attribute for effect in self.person.place_effects())

        self.assertIn(places_relations.ATTRIBUTE.TERRAIN_RADIUS, place_attributes)

    def test_place_effects__politic_radius_bonus(self):
        self.person.personality_cosmetic = relations.PERSONALITY_COSMETIC.TRUTH_SEEKER
        self.person.personality_practical = relations.PERSONALITY_PRACTICAL.ACTIVE
        self.person.refresh_attributes()

        place_attributes = set(effect.attribute for effect in self.person.place_effects())

        self.assertIn(places_relations.ATTRIBUTE.POLITIC_RADIUS, place_attributes)

    def test_place_effects__stability_renewing_bonus(self):
        self.person.personality_cosmetic = relations.PERSONALITY_COSMETIC.TRUTH_SEEKER
        self.person.personality_practical = relations.PERSONALITY_PRACTICAL.RELIABLE
        self.person.refresh_attributes()

        place_attributes = set(effect.attribute for effect in self.person.place_effects())

        self.assertIn(places_relations.ATTRIBUTE.STABILITY_RENEWING_SPEED, place_attributes)
