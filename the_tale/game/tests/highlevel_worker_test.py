# coding: utf-8
import mock

from dext.settings import settings

from common.utils import testcase

from accounts.logic import register_user

from game.persons.storage import persons_storage
from game.persons.models import Person, PERSON_STATE

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
        self.action_idl = self.storage.heroes_to_actions[self.hero.id][-1]

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

    def test_process_change_person_power(self):
        self.assertEqual(self.worker.persons_power, {})
        self.worker.process_change_person_power(person_id=0, power_delta=1)
        self.assertEqual(self.worker.persons_power, {0: 1})
        self.worker.process_change_person_power(person_id=1, power_delta=10)
        self.assertEqual(self.worker.persons_power, {0: 1, 1: 10})
        self.worker.process_change_person_power(person_id=0, power_delta=-100)
        self.assertEqual(self.worker.persons_power, {0: -99, 1: 10})

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

    def test_sync_data(self):
        from game.map.places.modifiers.prototypes import TradeCenter

        self.assertEqual(self.p1.power, 0)
        self.assertEqual(self.p2.power, 0)
        self.assertEqual(self.p3.power, 0)

        self.assertEqual(self.p1.modifier, None)
        self.p1.modifier = TradeCenter(self.p1)
        self.assertEqual(self.p1.modifier, TradeCenter(self.p1))

        persons_version_0 = persons_storage._version
        places_version_0 = places_storage._version

        self.assertEqual(Person.objects.filter(place_id=self.p1.id).count(), 2)
        self.assertEqual(Person.objects.filter(place_id=self.p2.id).count(), 3)
        self.assertEqual(Person.objects.filter(place_id=self.p3.id).count(), 3)
        self.assertEqual(len(persons_storage.all()), 8)

        self.worker.process_change_person_power(person_id=self.p1.persons[0].id, power_delta=1)
        self.worker.process_change_person_power(person_id=self.p2.persons[0].id, power_delta=100)
        self.worker.process_change_person_power(person_id=self.p2.persons[1].id, power_delta=1000)
        self.worker.process_change_person_power(person_id=self.p3.persons[0].id, power_delta=10000)
        self.worker.process_change_person_power(person_id=self.p3.persons[1].id, power_delta=100000)

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

        self.assertTrue(self.p1.size < self.p2.size)
        self.assertTrue(self.p2.size == self.p3.size) # since size changed only to +-1

        self.worker.process_change_person_power(person_id=self.p1.persons[0].id, power_delta=-10)
        self.worker.process_change_person_power(person_id=self.p2.persons[0].id, power_delta=-1)
        self.worker.process_change_person_power(person_id=self.p2.persons[0].id, power_delta=+10000000)
        self.worker.process_change_person_power(person_id=self.p3.persons[0].id, power_delta=-2)
        self.worker.process_change_person_power(person_id=self.p3.persons[1].id, power_delta=+20)

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

        self.assertTrue(self.p1.size < self.p3.size < self.p2.size)

        # test resulting persons list
        self.assertEqual(len(persons_storage.filter(state=PERSON_STATE.OUT_GAME)), 0) # now, persons removed by players throught bills
        self.assertEqual(Person.objects.filter(state=PERSON_STATE.OUT_GAME).count(), 0)
        self.assertEqual(len(persons_storage.filter(state=PERSON_STATE.IN_GAME)), 9)
        self.assertEqual(Person.objects.filter(state=PERSON_STATE.IN_GAME).count(), 9)

        # test persons by places
        self.assertEqual(Person.objects.filter(place_id=self.p1.id).count(), 2)
        self.assertEqual(Person.objects.filter(place_id=self.p2.id).count(), 4)
        self.assertEqual(Person.objects.filter(place_id=self.p3.id).count(), 3)

        self.assertTrue(len(set((persons_version_0, persons_version_1, persons_version_2))), 3)
        self.assertTrue(len(set((places_version_0, places_version_1, places_version_2))), 3)

        self.assertEqual(settings[persons_storage.SETTINGS_KEY], persons_version_2)
        self.assertEqual(settings[places_storage.SETTINGS_KEY], places_version_2)
