

import smart_imports

smart_imports.all()


class ChangeHeroTest(utils_testcase.TestCase):

    def setUp(self):
        super(ChangeHeroTest, self).setUp()

        game_logic.create_test_map()

        self.account = self.accounts_factory.create_account()
        self.storage = game_logic_storage.LogicStorage()
        self.storage.load_account_data(self.account.id)

        self.hero = self.storage.accounts_to_heroes[self.account.id]
        self.hero.utg_name.properties = self.hero.utg_name.properties.clone(self.hero.gender.utg_id)

        self.race = game_relations.RACE.ELF if game_relations.RACE.ELF != self.hero.race else game_relations.RACE.HUMAN
        self.gender = game_relations.GENDER.MALE if not self.hero.gender.is_MALE else game_relations.GENDER.FEMALE

        self.noun = game_names.generator().get_test_name(name='test_name', gender=self.gender)

    def tearDown(self):
        pass

    def test_create(self):
        task = postponed_tasks.ChangeHeroTask(self.hero.id, name=self.noun, race=self.race, gender=self.gender)
        self.assertEqual(task.state, postponed_tasks.CHANGE_HERO_TASK_STATE.UNPROCESSED)
        self.assertEqual(self.hero.preferences.place, None)

        self.assertEqual(task.name, self.noun)
        self.assertEqual(task.race, self.race)
        self.assertEqual(task.gender, self.gender)

    def test_serialization(self):
        task = postponed_tasks.ChangeHeroTask(self.hero.id, name=self.noun, race=self.race, gender=self.gender)
        self.assertEqual(task.serialize(), postponed_tasks.ChangeHeroTask.deserialize(task.serialize()).serialize())

    def test_check_change(self):
        task = postponed_tasks.ChangeHeroTask(self.hero.id, name=self.noun, race=self.race, gender=self.gender)
        self.assertNotEqual(self.hero.utg_name, self.noun)
        self.assertNotEqual(self.hero.gender, self.gender)
        self.assertNotEqual(self.hero.race, self.race)

        with mock.patch('the_tale.game.heroes.objects.Hero.reset_accessors_cache') as reset_accessors_cache:
            self.assertEqual(task.process(postponed_tasks_helpers.FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.SUCCESS)

        self.assertEqual(reset_accessors_cache.call_count, 1)

        self.assertEqual(task.state, postponed_tasks.CHANGE_HERO_TASK_STATE.PROCESSED)
        self.assertEqual(self.hero.utg_name.forms, self.noun.forms)
        self.assertEqual(self.hero.utg_name.properties.get(utg_relations.GENDER), self.gender.utg_id)
        self.assertEqual(self.hero.name, self.noun.normal_form())
        self.assertEqual(self.hero.race, self.race)
        self.assertEqual(self.hero.gender, self.gender)
