
import smart_imports

smart_imports.all()


class HeroDescriptionTests(utils_testcase.TestCase):

    def setUp(self):
        super().setUp()

        game_logic.create_test_map()

        account = self.accounts_factory.create_account(is_fast=True)

        self.storage = game_logic_storage.LogicStorage()
        self.storage.load_account_data(account)
        self.hero = self.storage.accounts_to_heroes[account.id]

    def test_no_description(self):
        self.assertEqual(logic.get_hero_description(self.hero.id), '')

    def test_has_description(self):
        logic.set_hero_description(self.hero.id, 'bla-bla')
        self.assertEqual(logic.get_hero_description(self.hero.id), 'bla-bla')

    def test_update_description(self):
        logic.set_hero_description(self.hero.id, 'bla-bla')
        logic.set_hero_description(self.hero.id, 'new description')
        self.assertEqual(logic.get_hero_description(self.hero.id), 'new description')


class CreateHero(utils_testcase.TestCase):

    def setUp(self):
        super().setUp()
        game_logic.create_test_map()

        self.account = accounts_prototypes.AccountPrototype.create(nick='nick-xxx',
                                                                   email='test@test.test',
                                                                   is_fast=False)

        self.attributes = {'is_fast': False,
                           'is_bot': False,
                           'might': 0,
                           'active_state_end_at': datetime.datetime.now() + datetime.timedelta(days=3),
                           'premium_state_end_at': datetime.datetime.fromtimestamp(0),
                           'ban_state_end_at': datetime.datetime.fromtimestamp(0)}

    def test_default(self):
        logic.create_hero(account_id=self.account.id, attributes=self.attributes)

        hero = logic.load_hero(self.account.id)

        self.assertEqual(hero.id, self.account.id)
        self.assertEqual(hero.account_id, self.account.id)

        self.assertIn(hero.gender, (game_relations.GENDER.MALE,
                                    game_relations.GENDER.FEMALE))
        self.assertEqual(hero.preferences.energy_regeneration_type, hero.race.energy_regeneration)
        self.assertEqual(hero.habit_honor.raw_value, 0)
        self.assertEqual(hero.habit_peacefulness.raw_value, 0)
        self.assertTrue(hero.preferences.archetype.is_NEUTRAL)
        self.assertTrue(hero.upbringing.is_PHILISTINE)
        self.assertTrue(hero.first_death.is_FROM_THE_MONSTER_FANGS)
        self.assertTrue(hero.death_age.is_MATURE)

    def test_account_attributes_required(self):
        for attribute in self.attributes.keys():
            with self.assertRaises(exceptions.HeroAttributeRequiredError):
                logic.create_hero(account_id=self.account.id,
                                  attributes={key: value for key, value in self.attributes.items() if key != attribute })

    def test_account_attributes(self):
        attributes = {'is_fast': random.choice((True, False)),
                      'is_bot': random.choice((True, False)),
                      'might': random.randint(1, 1000),
                      'active_state_end_at': datetime.datetime.fromtimestamp(1),
                      'premium_state_end_at': datetime.datetime.fromtimestamp(2),
                      'ban_state_end_at': datetime.datetime.fromtimestamp(3)}

        logic.create_hero(account_id=self.account.id, attributes=attributes)

        hero = logic.load_hero(self.account.id)

        self.assertEqual(hero.is_fast, attributes['is_fast'])
        self.assertEqual(hero.is_bot, attributes['is_bot'])
        self.assertEqual(hero.might, attributes['might'])
        self.assertEqual(hero.active_state_end_at, attributes['active_state_end_at'])
        self.assertEqual(hero.premium_state_end_at, attributes['premium_state_end_at'])
        self.assertEqual(hero.ban_state_end_at, attributes['ban_state_end_at'])

    def test_attributes(self):
        self.attributes.update({'race': game_relations.RACE.random(),
                                'gender': game_relations.GENDER.random(),
                                'name': game_names.generator().get_name(game_relations.RACE.random(),
                                                                        game_relations.GENDER.random()),
                                'peacefulness': random.randint(-c.HABITS_BORDER, c.HABITS_BORDER),
                                'honor': random.randint(-c.HABITS_BORDER, c.HABITS_BORDER),
                                'archetype': game_relations.ARCHETYPE.random(),
                                'upbringing': tt_beings_relations.UPBRINGING.random(),
                                'first_death': tt_beings_relations.FIRST_DEATH.random(),
                                'death_age': tt_beings_relations.AGE.random()})

        logic.create_hero(account_id=self.account.id, attributes=self.attributes)

        hero = logic.load_hero(self.account.id)

        self.assertEqual(hero.race, self.attributes['race'])
        self.assertEqual(hero.gender, self.attributes['gender'])
        self.assertEqual(hero.utg_name, self.attributes['name'])
        self.assertEqual(hero.habit_peacefulness.raw_value, self.attributes['peacefulness'])
        self.assertEqual(hero.habit_honor.raw_value, self.attributes['honor'])
        self.assertEqual(hero.preferences.archetype, self.attributes['archetype'])
        self.assertEqual(hero.upbringing, self.attributes['upbringing'])
        self.assertEqual(hero.first_death, self.attributes['first_death'])
        self.assertEqual(hero.death_age, self.attributes['death_age'])


class RegisterSpendingTests(utils_testcase.TestCase):

    def setUp(self):
        super().setUp()
        self.places = game_logic.create_test_map()

        account = self.accounts_factory.create_account()

        self.storage = game_logic_storage.LogicStorage()
        self.storage.load_account_data(account)
        self.hero = self.storage.accounts_to_heroes[account.id]

        self.hero.premium_state_end_at

        game_tt_services.debug_clear_service()

    @mock.patch('the_tale.game.heroes.objects.Hero.can_change_place_power', lambda hero, place: True)
    def test_not_in_place(self):
        self.hero.position.set_position(0, 0)
        self.assertEqual(self.hero.position.place_id, None)

        logic.register_spending(self.hero, 100)

        impacts = game_tt_services.money_impacts.cmd_get_targets_impacts(targets=[(tt_api_impacts.OBJECT_TYPE.PLACE, self.places[0].id)])

        self.assertEqual(impacts, [])

    @mock.patch('the_tale.game.heroes.objects.Hero.can_change_place_power', lambda hero, place: False)
    def test_can_not_change_place_power(self):
        self.hero.position.set_place(self.places[0])

        logic.register_spending(self.hero, 100)

        impacts = game_tt_services.money_impacts.cmd_get_targets_impacts(targets=[(tt_api_impacts.OBJECT_TYPE.PLACE, self.places[0].id)])

        self.assertEqual(impacts, [])

    @mock.patch('the_tale.game.heroes.objects.Hero.can_change_place_power', lambda hero, place: True)
    def test_can_change_place_power(self):
        self.hero.position.set_place(self.places[0])

        logic.register_spending(self.hero, 100)

        impacts = game_tt_services.money_impacts.cmd_get_targets_impacts(targets=[(tt_api_impacts.OBJECT_TYPE.PLACE, self.places[0].id)])

        self.assertEqual(len(impacts), 1)

        self.assertEqual(impacts[0].amount, 100)
        self.assertTrue(impacts[0].target_type.is_PLACE)
        self.assertEqual(impacts[0].target_id, self.places[0].id)

    @mock.patch('the_tale.game.heroes.objects.Hero.can_change_place_power', lambda hero, place: True)
    def test_can_change_place_power__below_zero(self):
        self.hero.position.set_place(self.places[0])

        logic.register_spending(self.hero, 100)
        logic.register_spending(self.hero, -50)

        impacts = game_tt_services.money_impacts.cmd_get_targets_impacts(targets=[(tt_api_impacts.OBJECT_TYPE.PLACE, self.places[0].id)])

        self.assertEqual(len(impacts), 1)

        self.assertEqual(impacts[0].amount, 150)


class GetPlacesPathModifiersTests(utils_testcase.TestCase):

    def setUp(self):
        super().setUp()

        self.places = game_logic.create_test_map()

        account = self.accounts_factory.create_account(is_fast=True)

        self.storage = game_logic_storage.LogicStorage()
        self.storage.load_account_data(account)
        self.hero = self.storage.accounts_to_heroes[account.id]

    def place_0_cost(self):
        return logic.get_places_path_modifiers(self.hero)[self.places[0].id]

    def test_every_place_has_modifier(self):
        modifiers = logic.get_places_path_modifiers(self.hero)
        self.assertEqual(set(modifiers.keys()), {place.id for place in self.places})

    def test_race_bonus(self):
        self.places[0].race = game_relations.RACE.random(exclude=(self.hero.race,))

        with self.check_almost_delta(self.place_0_cost, -c.PATH_MODIFIER_MINOR_DELTA):
            self.places[0].race = self.hero.race

    def test_modifier_bonus(self):
        self.assertFalse(self.places[0].is_modifier_active())

        with self.check_almost_delta(self.place_0_cost, -c.PATH_MODIFIER_MINOR_DELTA):
            self.places[0].set_modifier(places_modifiers.CITY_MODIFIERS.FORT)
            self.places[0].effects.add(game_effects.Effect(name='test',
                                                           attribute=places_relations.ATTRIBUTE.MODIFIER_FORT,
                                                           value=100500,
                                                           delta=0))
            self.places[0].refresh_attributes()

        self.assertTrue(self.places[0].is_modifier_active())

    def test_home_place(self):
        with self.check_almost_delta(self.place_0_cost, -c.PATH_MODIFIER_NORMAL_DELTA):
            self.hero.preferences.set(relations.PREFERENCE_TYPE.PLACE, self.places[0])

    def test_friend(self):
        with self.check_almost_delta(self.place_0_cost, -c.PATH_MODIFIER_NORMAL_DELTA):
            self.hero.preferences.set(relations.PREFERENCE_TYPE.FRIEND, self.places[0].persons[0])

    def test_enemy(self):
        with self.check_almost_delta(self.place_0_cost, c.PATH_MODIFIER_NORMAL_DELTA):
            self.hero.preferences.set(relations.PREFERENCE_TYPE.ENEMY, self.places[0].persons[0])

    def test_tax(self):
        self.places[0].attrs.size = 10
        self.places[0].refresh_attributes()
        self.assertEqual(self.places[0].attrs.tax, 0)

        with self.check_almost_delta(self.place_0_cost, c.PATH_MODIFIER_NORMAL_DELTA):
            self.places[0].effects.add(game_effects.Effect(name='test',
                                                           attribute=places_relations.ATTRIBUTE.TAX,
                                                           value=100,
                                                           delta=0))
            self.places[0].refresh_attributes()

    HABITS_DELTAS = [(-1, -1, -c.PATH_MODIFIER_MINOR_DELTA),
                     (-1,  0, 0),
                     (-1, +1, +c.PATH_MODIFIER_MINOR_DELTA),
                     ( 0, -1, 0),
                     ( 0,  0, 0),
                     ( 0, +1, 0),
                     (+1, -1, +c.PATH_MODIFIER_MINOR_DELTA),
                     (+1,  0, 0),
                     (+1, +1, -c.PATH_MODIFIER_MINOR_DELTA)]

    def test_habits__honor(self):
        for place_direction, hero_direction, expected_delta in self.HABITS_DELTAS:
            self.places[0].habit_honor.set_habit(0)
            self.hero.habit_honor.set_habit(0)

            with self.check_almost_delta(self.place_0_cost, expected_delta):
                self.places[0].habit_honor.set_habit(place_direction * c.HABITS_BORDER)
                self.hero.habit_honor.set_habit(hero_direction * c.HABITS_BORDER)

    def test_habits__peacefulness(self):
        for place_direction, hero_direction, expected_delta in self.HABITS_DELTAS:
            self.places[0].habit_peacefulness.set_habit(0)
            self.hero.habit_peacefulness.set_habit(0)

            with self.check_almost_delta(self.place_0_cost, expected_delta):
                self.places[0].habit_peacefulness.set_habit(place_direction * c.HABITS_BORDER)
                self.hero.habit_peacefulness.set_habit(hero_direction * c.HABITS_BORDER)
