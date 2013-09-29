# coding: utf-8
import mock
import contextlib

from dext.settings import settings

from common.utils import testcase

from accounts.logic import register_user

from game.persons.storage import persons_storage
from game.persons.models import Person

from game.heroes.prototypes import HeroPrototype

from game.map.places.storage import places_storage

from game.balance import constants as c
from game.logic import create_test_map
from game.workers.environment import workers_environment
from game.prototypes import TimePrototype
from game.bills.conf import bills_settings
from game.logic_storage import LogicStorage

def fake_sync_data(self):
    self._data_synced = True

def fake_apply_bills(self):
    if not hasattr(self, '_bills_applied'):
        self._bills_applied = 0
    self._bills_applied += 1


class HighlevelTest(testcase.TestCase):

    def setUp(self):
        super(HighlevelTest, self).setUp()

        self.p1, self.p2, self.p3 = create_test_map()

        result, account_id, bundle_id = register_user('test_user')

        self.hero = HeroPrototype.get_by_account_id(account_id)
        self.storage = LogicStorage()
        self.storage.add_hero(self.hero)
        self.action_idl = self.hero.actions.current_action

        workers_environment.deinitialize()
        workers_environment.initialize()

        self.worker = workers_environment.highlevel
        self.worker.process_initialize(TimePrototype.get_current_turn_number(), 'highlevel')

    def tearDown(self):
        pass

    def test_process_initialize(self):
        self.assertTrue(self.worker.initialized)
        self.assertEqual(self.worker.worker_id, 'highlevel')
        self.assertEqual(self.worker.turn_number, 0)
        self.assertEqual(self.worker.persons_power, {})

    def test_process_change_power(self):
        self.assertEqual(self.worker.persons_power, {})
        self.worker.process_change_power(person_id=0, power_delta=1, place_id=None)
        self.assertEqual(self.worker.persons_power, {0: 1})
        self.worker.process_change_power(person_id=1, power_delta=10, place_id=None)
        self.assertEqual(self.worker.persons_power, {0: 1, 1: 10})
        self.worker.process_change_power(person_id=0, power_delta=-100, place_id=None)
        self.assertEqual(self.worker.persons_power, {0: -99, 1: 10})

        self.assertEqual(self.worker.places_power, {})
        self.worker.process_change_power(person_id=None, power_delta=1, place_id=2)
        self.assertEqual(self.worker.places_power, {2: 1})
        self.worker.process_change_power(person_id=None, power_delta=10, place_id=1)
        self.assertEqual(self.worker.places_power, {2: 1, 1: 10})
        self.worker.process_change_power(person_id=None, power_delta=-100, place_id=2)
        self.assertEqual(self.worker.places_power, {2: -99, 1: 10})

    @mock.patch('game.workers.highlevel.Worker.sync_data', fake_sync_data)
    @mock.patch('game.workers.highlevel.Worker.apply_bills', fake_apply_bills)
    @mock.patch('subprocess.call', lambda x: None)
    @mock.patch('game.balance.constants.MAP_SYNC_TIME', 10)
    def test_process_next_turn(self):

        time = TimePrototype.get_current_time()
        time.increment_turn()
        time.save()

        self.assertEqual(time.turn_number, 1)

        for i in xrange(c.MAP_SYNC_TIME-1):
            self.worker.process_next_turn(time.turn_number)
            self.assertFalse(hasattr(self.worker, '_data_synced'))

            if time.turn_number < bills_settings.BILLS_PROCESS_INTERVAL / c.TURN_DELTA:
                self.assertFalse(hasattr(self.worker, '_bills_applied'))
            else:
                self.assertEqual(self.worker._bills_applied, time.turn_number / (bills_settings.BILLS_PROCESS_INTERVAL / c.TURN_DELTA))

            time.increment_turn()
            time.save()

        self.worker.process_next_turn(time.turn_number)
        self.assertTrue(self.worker._data_synced)


    @mock.patch('game.workers.highlevel.Worker.sync_data', fake_sync_data)
    @mock.patch('subprocess.call', lambda x: None)
    def test_process_stop(self):
        self.worker.process_stop()
        self.assertTrue(self.worker._data_synced)
        self.assertFalse(self.worker.initialized)
        self.assertTrue(self.worker.stop_required)

    def test_sync_data__places_methods_called(self):
        # all that methods tested in places package
        set_expected_size = mock.Mock()
        sync_size = mock.Mock()
        sync_persons = mock.Mock()
        sync_modifier = mock.Mock()
        sync_parameters = mock.Mock()
        update_heroes_number = mock.Mock()
        mark_as_updated = mock.Mock()

        with contextlib.nested(mock.patch('game.map.places.prototypes.PlacePrototype.set_expected_size', set_expected_size),
                               mock.patch('game.map.places.prototypes.PlacePrototype.sync_size', sync_size),
                               mock.patch('game.map.places.prototypes.PlacePrototype.sync_persons', sync_persons),
                               mock.patch('game.map.places.prototypes.PlacePrototype.sync_modifier', sync_modifier),
                               mock.patch('game.map.places.prototypes.PlacePrototype.sync_parameters', sync_parameters),
                               mock.patch('game.map.places.prototypes.PlacePrototype.update_heroes_number', update_heroes_number),
                               mock.patch('game.map.places.prototypes.PlacePrototype.mark_as_updated', mark_as_updated)):
            self.worker.sync_data()

        places_number = len(places_storage.all())

        self.assertEqual(set_expected_size.call_count, places_number)
        self.assertEqual(sync_size.call_count, places_number)
        self.assertEqual(sync_persons.call_count, places_number)
        self.assertEqual(sync_modifier.call_count, places_number)
        self.assertEqual(sync_parameters.call_count, places_number)
        self.assertEqual(update_heroes_number.call_count, places_number)
        self.assertEqual(mark_as_updated.call_count, places_number)

    @mock.patch('game.map.places.prototypes.PlacePrototype.freedom', 1)
    @mock.patch('game.map.places.prototypes.PlacePrototype.sync_parameters', mock.Mock())
    def test_sync_data(self):
        self.assertEqual(self.p1.power, 0)
        self.assertEqual(self.p2.power, 0)
        self.assertEqual(self.p3.power, 0)

        persons_version_0 = persons_storage._version
        places_version_0 = places_storage._version

        self.assertEqual(Person.objects.filter(place_id=self.p1.id).count(), 2)
        self.assertEqual(Person.objects.filter(place_id=self.p2.id).count(), 3)
        self.assertEqual(Person.objects.filter(place_id=self.p3.id).count(), 3)
        self.assertEqual(len(persons_storage.all()), 8)

        self.worker.process_change_power(person_id=self.p1.persons[0].id, power_delta=1, place_id=None)
        self.worker.process_change_power(person_id=self.p2.persons[0].id, power_delta=100, place_id=None)
        self.worker.process_change_power(person_id=self.p2.persons[1].id, power_delta=1000, place_id=None)
        self.worker.process_change_power(person_id=self.p3.persons[0].id, power_delta=10000, place_id=None)
        self.worker.process_change_power(person_id=self.p3.persons[1].id, power_delta=100000, place_id=None)

        self.assertEqual(self.p1.power, 0)
        self.assertEqual(self.p2.power, 0)
        self.assertEqual(self.p3.power, 0)

        self.worker.sync_data()
        self.assertEqual(self.worker.persons_power, {})

        self.assertEqual(self.p1.modifier, None)

        persons_version_1 = persons_storage._version
        places_version_1 = places_storage._version

        self.assertEqual(self.p1.power, 1)
        self.assertEqual(self.p2.power, 1100)
        self.assertEqual(self.p3.power, 110000)

        self.worker.process_change_power(place_id=self.p1.id, power_delta=-10, person_id=None)
        self.worker.process_change_power(place_id=self.p2.id, power_delta=-1, person_id=None)
        self.worker.process_change_power(place_id=self.p2.id, power_delta=+10000000, person_id=None)
        self.worker.process_change_power(place_id=self.p3.id, power_delta=-2, person_id=None)
        self.worker.process_change_power(place_id=self.p3.id, power_delta=+20, person_id=None)

        self.worker.sync_data()
        self.assertEqual(self.worker.persons_power, {})

        persons_version_2 = persons_storage._version
        places_version_2 = places_storage._version

        self.p1 = places_storage[self.p1.id]
        self.p2 = places_storage[self.p2.id]
        self.p3 = places_storage[self.p3.id]

        self.assertEqual(self.p1.power, 0)
        self.assertEqual(self.p2.power, 10001099)
        self.assertEqual(self.p3.power, 110018)

        self.assertTrue(len(set((persons_version_0, persons_version_1, persons_version_2))), 3)
        self.assertTrue(len(set((places_version_0, places_version_1, places_version_2))), 3)

        self.assertEqual(settings[persons_storage.SETTINGS_KEY], persons_version_2)
        self.assertEqual(settings[places_storage.SETTINGS_KEY], places_version_2)


    @mock.patch('game.map.places.prototypes.PlacePrototype.freedom', 1)
    @mock.patch('game.map.places.prototypes.PlacePrototype.sync_parameters', mock.Mock())
    def test_sync_data__power_from_building(self):
        from textgen import words
        from game.map.places.prototypes import BuildingPrototype

        person_1 = self.p1.persons[0]

        BuildingPrototype.create(person_1, name_forms=words.Noun.fast_construct(u'noun'))

        self.assertEqual(self.p1.power, 0)
        self.assertEqual(person_1.power, 0)

        self.worker.process_change_power(person_id=person_1.id, power_delta=1000, place_id=None)

        self.worker.sync_data()

        place_power = self.p1.power
        person_power = person_1.power

        self.assertTrue(place_power > 1000)
        self.assertTrue(person_power > 1000)

        self.worker.process_change_power(place_id=self.p1.id, power_delta=-10, person_id=None)

        self.worker.sync_data()

        self.assertEqual(self.p1.power, place_power - 10)
        self.assertEqual(person_1.power, person_power)

    @mock.patch('game.map.places.prototypes.PlacePrototype.freedom', 1.25)
    @mock.patch('game.map.places.prototypes.PlacePrototype.sync_parameters', mock.Mock())
    def test_sync_data__power_from_freedom(self):
        person_1 = self.p1.persons[0]

        self.assertEqual(self.p1.power, 0)
        self.assertEqual(person_1.power, 0)

        self.worker.process_change_power(person_id=person_1.id, power_delta=1000, place_id=None)

        self.worker.sync_data()

        self.assertEqual(self.p1.power, 1250)
        self.assertEqual(person_1.power, 1250)

        self.worker.process_change_power(place_id=self.p1.id, power_delta=-100, person_id=None)

        self.worker.sync_data()

        self.assertEqual(self.p1.power, 1125)
        self.assertEqual(person_1.power, 1250)
