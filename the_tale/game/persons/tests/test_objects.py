# coding: utf-8
import mock

from the_tale.common.utils import testcase

from the_tale.game import names

from the_tale.game.prototypes import TimePrototype
from the_tale.game.logic import create_test_map

from the_tale.game.heroes import logic as heroes_logic

from the_tale.game.places.prototypes import BuildingPrototype

from the_tale.game.persons.tests.helpers import create_person


class PersonTests(testcase.TestCase):

    def setUp(self):
        super(PersonTests, self).setUp()
        current_time = TimePrototype.get_current_time()
        current_time.increment_turn()

        self.persons_changed_at_turn = TimePrototype.get_current_turn_number()

        self.p1, self.p2, self.p3 = create_test_map()

        self.person = create_person(self.p1)

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

    def test_power_from_building(self):

        with mock.patch('the_tale.game.workers.highlevel.Worker.cmd_change_power') as change_person_power_call:
            self.person.cmd_change_power(hero_id=666, has_place_in_preferences=False, has_person_in_preferences=False, power=100)

        self.assertEqual(change_person_power_call.call_args, mock.call(hero_id=666,
                                                                       has_place_in_preferences=False,
                                                                       has_person_in_preferences=False,
                                                                       person_id=self.person.id,
                                                                       power_delta=100,
                                                                       place_id=None))

        BuildingPrototype.create(self.person, utg_name=names.generator.get_test_name('building-name'))

        with mock.patch('the_tale.game.workers.highlevel.Worker.cmd_change_power') as change_person_power_call:
            self.person.cmd_change_power(hero_id=666, has_place_in_preferences=False, has_person_in_preferences=False, power=-100)

        self.assertEqual(change_person_power_call.call_args, mock.call(hero_id=666,
                                                                       has_place_in_preferences=False,
                                                                       has_person_in_preferences=False,
                                                                       person_id=self.person.id,
                                                                       power_delta=-100,
                                                                       place_id=None))
