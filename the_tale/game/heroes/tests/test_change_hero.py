# coding: utf-8
import mock

from utg import relations as utg_relations

from the_tale.common.utils.testcase import TestCase
from the_tale.common.postponed_tasks import FakePostpondTaskPrototype, POSTPONED_TASK_LOGIC_RESULT

from the_tale.accounts.prototypes import AccountPrototype
from the_tale.accounts.logic import register_user

from the_tale.game.logic import create_test_map
from the_tale.game.relations import GENDER, RACE
from the_tale.game.logic_storage import LogicStorage

from the_tale.game import names

from the_tale.game.heroes.postponed_tasks import ChangeHeroTask, CHANGE_HERO_TASK_STATE


class ChangeHeroTest(TestCase):

    def setUp(self):
        super(ChangeHeroTest, self).setUp()
        place_1, place_2, place_3 = create_test_map()

        result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')
        self.account = AccountPrototype.get_by_id(account_id)
        self.storage = LogicStorage()
        self.storage.load_account_data(self.account)

        self.hero = self.storage.accounts_to_heroes[account_id]
        self.hero.utg_name.properties = self.hero.utg_name.properties.clone(self.hero.gender.utg_id)

        self.noun = names.generator.get_test_name(name='test_name', gender=GENDER.NEUTER)

        self.race = RACE.ELF if RACE.ELF != self.hero.race else RACE.HUMAN
        self.gender = GENDER.NEUTER if not self.hero.gender.is_NEUTER else GENDER.FEMININE

    def tearDown(self):
        pass

    def test_create(self):
        task = ChangeHeroTask(self.hero.id, name=self.noun, race=self.race, gender=self.gender)
        self.assertEqual(task.state, CHANGE_HERO_TASK_STATE.UNPROCESSED)
        self.assertEqual(self.hero.preferences.place, None)

        self.assertEqual(task.name, self.noun)
        self.assertEqual(task.race, self.race)
        self.assertEqual(task.gender, self.gender)

    def test_serialization(self):
        task = ChangeHeroTask(self.hero.id, name=self.noun, race=self.race, gender=self.gender)
        self.assertEqual(task.serialize(), ChangeHeroTask.deserialize(task.serialize()).serialize())

    def test_check_change(self):
        task = ChangeHeroTask(self.hero.id, name=self.noun, race=self.race, gender=self.gender)
        self.assertNotEqual(self.hero.utg_name, self.noun)
        self.assertNotEqual(self.hero.gender, self.gender)
        self.assertNotEqual(self.hero.race, self.race)
        self.assertFalse(self.hero.settings_approved)

        with mock.patch('the_tale.game.heroes.objects.Hero.reset_accessors_cache') as reset_accessors_cache:
            self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.SUCCESS)

        self.assertEqual(reset_accessors_cache.call_count, 1)

        self.assertEqual(task.state, CHANGE_HERO_TASK_STATE.PROCESSED)
        self.assertEqual(self.hero.utg_name.forms, self.noun.forms)
        self.assertEqual(self.hero.utg_name.properties.get(utg_relations.GENDER), self.gender.utg_id)
        self.assertEqual(self.hero.name, self.noun.normal_form())
        self.assertEqual(self.hero.race, self.race)
        self.assertEqual(self.hero.gender, self.gender)
        self.assertTrue(self.hero.settings_approved)
