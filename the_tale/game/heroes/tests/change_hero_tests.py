# coding: utf-8

from textgen.words import Noun

from common.utils.testcase import TestCase

from accounts.prototypes import AccountPrototype
from accounts.logic import register_user

from game.logic import create_test_map
from game.game_info import RACE, GENDER
from game.logic_storage import LogicStorage

from game.heroes.prototypes import ChangeHeroTaskPrototype
from game.heroes.models import ChangeHeroTask, CHANGE_HERO_STATE


class ChangeHeroTest(TestCase):

    def setUp(self):
        place_1, place_2, place_3 = create_test_map()

        result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')
        self.account = AccountPrototype.get_by_id(account_id)
        self.storage = LogicStorage()
        self.storage.load_account_data(self.account)

        self.hero = self.storage.accounts_to_heroes[account_id]

        self.noun = Noun(normalized=u'слово', forms=[u'слово', u'слова', u'слову', u'слово', u'словом', u'слове',
                                                     u'слово', u'слова', u'слову', u'слово', u'словом', u'слове'], properties=(u'ср', ))
        self.forms=[u'слово', u'слова', u'слову', u'слово', u'словом', u'слове']

        self.race = RACE.ELF if RACE.ELF != self.hero.race else RACE.HUMAN
        self.gender = GENDER.NEUTER if GENDER.NEUTER != self.hero.gender else GENDER.FEMININE

    def tearDown(self):
        pass

    def test_create(self):
        self.assertEqual(ChangeHeroTask.objects.all().count(), 0)
        task = ChangeHeroTaskPrototype.create(self.hero, forms=self.forms, race=self.race, gender=self.gender)
        self.assertEqual(ChangeHeroTask.objects.all().count(), 1)
        self.assertEqual(task.state, CHANGE_HERO_STATE.WAITING)
        self.assertEqual(self.hero.preferences.place_id, None)

        self.assertEqual(task.name, self.noun)
        self.assertEqual(task.race, self.race)
        self.assertEqual(task.gender, self.gender)

    def test_reset_all(self):
        ChangeHeroTaskPrototype.create(self.hero, forms=self.forms, race=self.race, gender=self.gender)
        self.assertEqual(ChangeHeroTask.objects.filter(state=CHANGE_HERO_STATE.WAITING).count(), 1)
        ChangeHeroTaskPrototype.reset_all()
        self.assertEqual(ChangeHeroTask.objects.filter(state=CHANGE_HERO_STATE.WAITING).count(), 0)
        self.assertEqual(ChangeHeroTask.objects.filter(state=CHANGE_HERO_STATE.RESET).count(), 1)

    def test_check_change(self):
        task = ChangeHeroTaskPrototype.create(self.hero, forms=self.forms, race=self.race, gender=self.gender)
        self.assertNotEqual(self.hero.normalized_name, self.noun)
        self.assertNotEqual(self.hero.gender, self.gender)
        self.assertNotEqual(self.hero.race, self.race)
        self.assertFalse(self.hero.is_name_changed)

        task.process(self.storage)

        self.assertEqual(task.state, CHANGE_HERO_STATE.PROCESSED)
        self.assertEqual(self.hero.normalized_name, self.noun)
        self.assertEqual(self.hero.name, self.noun.normalized)
        self.assertEqual(self.hero.race, self.race)
        self.assertEqual(self.hero.gender, self.gender)
        self.assertTrue(self.hero.is_name_changed)
