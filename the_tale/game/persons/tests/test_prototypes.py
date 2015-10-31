# coding: utf-8
import mock
import datetime

from the_tale.common.utils import testcase

from the_tale.accounts.logic import register_user

from the_tale.game import names

from the_tale.game.prototypes import TimePrototype
from the_tale.game.logic import create_test_map

from the_tale.game.heroes import logic as heroes_logic

from the_tale.game.map.places.prototypes import BuildingPrototype

from the_tale.game.persons.relations import PERSON_STATE
from the_tale.game.persons.tests.helpers import create_person

class PrototypeTests(testcase.TestCase):

    def setUp(self):
        super(PrototypeTests, self).setUp()
        current_time = TimePrototype.get_current_time()
        current_time.increment_turn()

        self.persons_changed_at_turn = TimePrototype.get_current_turn_number()

        self.p1, self.p2, self.p3 = create_test_map()

        self.person = create_person(self.p1, PERSON_STATE.IN_GAME)

        account = self.accounts_factory.create_account()
        self.hero_1 = heroes_logic.load_hero(account_id=account.id)

        account = self.accounts_factory.create_account()
        self.hero_2 = heroes_logic.load_hero(account_id=account.id)

        account = self.accounts_factory.create_account()
        self.hero_3 = heroes_logic.load_hero(account_id=account.id)

        current_time = TimePrototype.get_current_time()
        current_time.increment_turn()


    def test_initialize(self):
        self.assertEqual(self.person.place.persons_changed_at_turn, self.persons_changed_at_turn)

        self.assertEqual(self.person.friends_number, 0)
        self.assertEqual(self.person.enemies_number, 0)
        self.assertEqual(self.person.created_at_turn, TimePrototype.get_current_turn_number() - 1)
        self.assertTrue(self.person.is_stable)

    @mock.patch('the_tale.game.persons.conf.settings.POWER_STABILITY_PERCENT', 1.0)
    @mock.patch('the_tale.game.persons.conf.settings.POWER_STABILITY_WEEKS', -1.0)
    def test_is_stable_no_time_delay_no_percent(self):
        self.assertFalse(self.person.is_stable)

    @mock.patch('the_tale.game.persons.conf.settings.POWER_STABILITY_PERCENT', 1.0)
    @mock.patch('the_tale.game.persons.conf.settings.POWER_STABILITY_WEEKS', 10.0)
    def test_is_stable_with_time_delay(self):
        self.assertTrue(self.person.is_stable)

    @mock.patch('the_tale.game.persons.conf.settings.POWER_STABILITY_PERCENT', -1.0)
    @mock.patch('the_tale.game.persons.conf.settings.POWER_STABILITY_WEEKS', -1.0)
    def test_is_stable_with_percent(self):
        self.assertTrue(self.person.is_stable)

    def test_move_out_game(self):
        self.assertEqual(self.person.place.persons_changed_at_turn, self.persons_changed_at_turn)

        TimePrototype.get_current_time().increment_turn()

        current_time = datetime.datetime.now()
        self.assertTrue(self.person.out_game_at < current_time)
        self.assertEqual(self.person.state, PERSON_STATE.IN_GAME)
        self.person.move_out_game()
        self.assertTrue(self.person.out_game_at > current_time)
        self.assertEqual(self.person.state, PERSON_STATE.OUT_GAME)

        self.assertEqual(self.person.place.persons_changed_at_turn, TimePrototype.get_current_turn_number())

    def test_move_out_game_with_building(self):
        building = BuildingPrototype.create(self.person, utg_name=names.generator.get_test_name('building-name'))
        self.assertTrue(building.state.is_WORKING)
        self.person.move_out_game()
        self.assertTrue(building.state.is_DESTROYED)

    def test_mastery_from_building(self):

        while True:
            person = create_person(self.p1, PERSON_STATE.IN_GAME)
            old_mastery = person.mastery

            if old_mastery < 0.8:
                break

        building = BuildingPrototype.create(person, utg_name=names.generator.get_test_name('building-name'))

        max_mastery = person.mastery

        building._model.integrity = 0.5

        self.assertTrue(old_mastery < person.mastery < max_mastery)

    def test_power_from_building(self):

        with mock.patch('the_tale.game.workers.highlevel.Worker.cmd_change_power') as change_person_power_call:
            self.person.cmd_change_power(100, 1, 2)

        self.assertEqual(change_person_power_call.call_args, mock.call(person_id=self.person.id, power_delta=100, place_id=None, positive_bonus=1, negative_bonus=2))

        BuildingPrototype.create(self.person, utg_name=names.generator.get_test_name('building-name'))

        with mock.patch('the_tale.game.workers.highlevel.Worker.cmd_change_power') as change_person_power_call:
            self.person.cmd_change_power(100, -2, -1)

        self.assertEqual(change_person_power_call.call_args, mock.call(person_id=self.person.id, power_delta=100, place_id=None, positive_bonus=-2, negative_bonus=-1))
