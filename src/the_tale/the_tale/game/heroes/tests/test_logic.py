
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
