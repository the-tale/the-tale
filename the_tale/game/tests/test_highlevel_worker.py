# coding: utf-8
import mock
import contextlib

from dext.settings import settings

from the_tale.amqp_environment import environment

from the_tale.common.utils import testcase

from the_tale.game import names

from the_tale.game.bills import bills
from the_tale.game.bills import prototypes as bills_prototypes

from the_tale.game.persons import storage as persons_storage
from the_tale.game.persons.models import Person

from the_tale.game.places import storage as places_storage

from the_tale.game.balance import constants as c
from the_tale.game.logic import create_test_map
from the_tale.game.prototypes import TimePrototype
from the_tale.game.bills.conf import bills_settings
from the_tale.game.logic_storage import LogicStorage

from the_tale.game.workers import highlevel


def fake_sync_data(self, sheduled=True):
    self._data_synced = True

def fake_apply_bills(self):
    if not hasattr(self, '_bills_applied'):
        self._bills_applied = 0
    self._bills_applied += 1


class HighlevelTest(testcase.TestCase):

    def setUp(self):
        super(HighlevelTest, self).setUp()

        self.p1, self.p2, self.p3 = create_test_map()

        self.account = self.accounts_factory.create_account()

        self.storage = LogicStorage()
        self.storage.load_account_data(self.account)
        self.hero = self.storage.accounts_to_heroes[self.account.id]
        self.action_idl = self.hero.actions.current_action

        environment.deinitialize()
        environment.initialize()

        self.worker = environment.workers.highlevel
        self.worker.process_initialize(TimePrototype.get_current_turn_number(), 'highlevel')

    def tearDown(self):
        pass

    def test_process_initialize(self):
        self.assertTrue(self.worker.initialized)
        self.assertEqual(self.worker.worker_id, 'highlevel')
        self.assertEqual(self.worker.turn_number, 0)
        self.assertEqual(self.worker.places_politic_power, [])
        self.assertEqual(self.worker.persons_politic_power, [])

    def test_process_change_power__persons(self):
        self.assertEqual(self.worker.persons_politic_power, [])

        person_1, person_2 = persons_storage.persons.all()[0:2]

        power_info_1 = highlevel.PowerInfo(hero_id=666,
                                           has_place_in_preferences=True,
                                           has_person_in_preferences=False,
                                           person_id=person_1.id,
                                           place_id=None,
                                           power_delta=1)

        self.worker.process_change_power(**power_info_1.kwargs)

        self.assertEqual(self.worker.persons_politic_power, [power_info_1])

        power_info_2 = highlevel.PowerInfo(hero_id=777,
                                           has_place_in_preferences=False,
                                           has_person_in_preferences=True,
                                           person_id=person_2.id,
                                           place_id=None,
                                           power_delta=10)

        self.worker.process_change_power(**power_info_2.kwargs)
        self.assertEqual(self.worker.persons_politic_power, [power_info_1, power_info_2])

        power_info_3 = highlevel.PowerInfo(hero_id=None,
                                           has_place_in_preferences=False,
                                           has_person_in_preferences=False,
                                           person_id=person_1.id,
                                           place_id=None,
                                           power_delta=-100)

        self.worker.process_change_power(**power_info_3.kwargs)
        self.assertEqual(self.worker.persons_politic_power, [power_info_1, power_info_2, power_info_3])

        self.assertEqual(person_1.politic_power.inner_power, 0)
        self.assertEqual(person_1.politic_power.outer_power, 0)
        self.assertEqual(person_2.politic_power.inner_power, 0)
        self.assertEqual(person_2.politic_power.outer_power, 0)


    def test_process_change_power__places(self):
        self.assertEqual(self.worker.places_politic_power, [])

        place_1, place_2 = places_storage.places.all()[0:2]

        power_info_1 = highlevel.PowerInfo(hero_id=666,
                                           has_place_in_preferences=True,
                                           has_person_in_preferences=False,
                                           person_id=None,
                                           place_id=place_1.id,
                                           power_delta=1)

        self.worker.process_change_power(**power_info_1.kwargs)

        self.assertEqual(self.worker.places_politic_power, [power_info_1])

        power_info_2 = highlevel.PowerInfo(hero_id=777,
                                           has_place_in_preferences=False,
                                           has_person_in_preferences=True,
                                           person_id=None,
                                           place_id=place_2.id,
                                           power_delta=10)

        self.worker.process_change_power(**power_info_2.kwargs)
        self.assertEqual(self.worker.places_politic_power, [power_info_1, power_info_2])

        power_info_3 = highlevel.PowerInfo(hero_id=None,
                                           has_place_in_preferences=False,
                                           has_person_in_preferences=False,
                                           person_id=None,
                                           place_id=place_1.id,
                                           power_delta=-100)

        self.worker.process_change_power(**power_info_3.kwargs)
        self.assertEqual(self.worker.places_politic_power, [power_info_1, power_info_2, power_info_3])

        self.assertEqual(place_1.politic_power.inner_power, 0)
        self.assertEqual(place_1.politic_power.outer_power, 0)
        self.assertEqual(place_2.politic_power.inner_power, 0)
        self.assertEqual(place_2.politic_power.outer_power, 0)


    @mock.patch('the_tale.game.workers.highlevel.Worker.sync_data', fake_sync_data)
    @mock.patch('the_tale.game.workers.highlevel.Worker.apply_bills', fake_apply_bills)
    @mock.patch('subprocess.call', lambda x: None)
    @mock.patch('the_tale.game.balance.constants.MAP_SYNC_TIME', 10)
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


    @mock.patch('the_tale.game.bills.conf.bills_settings.MIN_VOTES_PERCENT', 0)
    @mock.patch('the_tale.game.bills.conf.bills_settings.BILL_LIVE_TIME', 0)
    def test_apply_bills__stop_bill_without_meaning(self):
        from the_tale.forum.models import Category, SubCategory

        forum_category = Category.objects.create(caption='category-1', slug='category-1')
        SubCategory.objects.create(caption=bills_settings.FORUM_CATEGORY_UID + '-caption',
                                   uid=bills_settings.FORUM_CATEGORY_UID,
                                   category=forum_category)

        new_name = names.generator.get_test_name('new-new-name')

        bill_data_1 = bills.PlaceRenaming(place_id=self.p1.id, name_forms=new_name)
        bill_1 = bills_prototypes.BillPrototype.create(self.account, 'bill-1-caption', 'bill-1-rationale', bill_data_1, chronicle_on_accepted='chronicle-on-accepted')
        bill_1.approved_by_moderator = True
        bill_1.save()

        bill_data_2 = bills.PlaceRenaming(place_id=self.p1.id, name_forms=new_name)
        bill_2 = bills_prototypes.BillPrototype.create(self.account, 'bill-2-caption', 'bill-2-rationale', bill_data_2, chronicle_on_accepted='chronicle-on-accepted')
        bill_2.approved_by_moderator = True
        bill_2.save()

        self.worker.apply_bills()

        bill_1.reload()
        bill_2.reload()

        self.assertTrue(bill_1.state.is_ACCEPTED)
        self.assertTrue(bill_2.state.is_STOPPED)


    @mock.patch('the_tale.game.workers.highlevel.Worker.sync_data', fake_sync_data)
    @mock.patch('subprocess.call', lambda x: None)
    def test_process_stop(self):
        self.worker.process_stop()
        self.assertTrue(self.worker._data_synced)
        self.assertFalse(self.worker.initialized)
        self.assertTrue(self.worker.stop_required)

    def test_sync_data__places_methods_called(self):
        # all that methods tested in places package
        set_power_economic = mock.Mock()
        sync_size = mock.Mock()
        update_step = mock.Mock()
        sync_habits = mock.Mock()
        refresh_attributes = mock.Mock()
        mark_as_updated = mock.Mock()

        with contextlib.nested(mock.patch('the_tale.game.places.attributes.Attributes.set_power_economic', set_power_economic),
                               mock.patch('the_tale.game.places.attributes.Attributes.sync_size', sync_size),
                               mock.patch('the_tale.game.places.objects.Place.effects', mock.Mock(update_step=update_step, effects=[], serialize=lambda: {})),
                               mock.patch('the_tale.game.places.objects.Place.sync_habits', sync_habits),
                               mock.patch('the_tale.game.places.objects.Place.refresh_attributes', refresh_attributes),
                               mock.patch('the_tale.game.places.objects.Place.mark_as_updated', mark_as_updated)):
            self.worker.sync_data()

        places_number = len(places_storage.places.all())

        self.assertEqual(set_power_economic.call_count, places_number)
        self.assertEqual(sync_size.call_count, places_number)
        self.assertEqual(sync_habits.call_count, places_number)
        self.assertEqual(refresh_attributes.call_count, places_number)
        self.assertEqual(mark_as_updated.call_count, places_number)


    def test_sync_data__social_connections_synced(self):
        with self.check_increased(lambda: len(persons_storage.social_connections.all())):
            self.worker.sync_data()

    @mock.patch('the_tale.game.balance.constants.PLACE_POWER_REDUCE_FRACTION', 0.9)
    @mock.patch('the_tale.game.places.objects.Place.refresh_attributes', mock.Mock())
    def test_sync_data(self):
        self.assertEqual(self.p1.politic_power.outer_power, 0)
        self.assertEqual(self.p1.politic_power.inner_power, 0)
        self.assertEqual(self.p2.politic_power.outer_power, 0)
        self.assertEqual(self.p2.politic_power.inner_power, 0)
        self.assertEqual(self.p3.politic_power.outer_power, 0)
        self.assertEqual(self.p3.politic_power.inner_power, 0)

        self.assertEqual(Person.objects.filter(place_id=self.p1.id).count(), 3)
        self.assertEqual(Person.objects.filter(place_id=self.p2.id).count(), 3)
        self.assertEqual(Person.objects.filter(place_id=self.p3.id).count(), 3)
        self.assertEqual(len(persons_storage.persons.all()), 9)

        person_1_1 = self.p1.persons[0]
        person_2_1 = self.p2.persons[0]
        person_2_2 = self.p2.persons[1]
        person_3_1 = self.p3.persons[0]
        person_3_2 = self.p3.persons[1]

        power_info = highlevel.PowerInfo(hero_id=666,
                                         has_place_in_preferences=False,
                                         has_person_in_preferences=False,
                                         person_id=None,
                                         place_id=None,
                                         power_delta=0)


        self.worker.process_change_power(**power_info.clone(person_id=person_1_1.id, power_delta=1).kwargs)
        self.worker.process_change_power(**power_info.clone(person_id=person_2_1.id, power_delta=100).kwargs)
        self.worker.process_change_power(**power_info.clone(person_id=person_2_2.id, power_delta=1000).kwargs)
        self.worker.process_change_power(**power_info.clone(person_id=person_3_1.id, power_delta=10000).kwargs)
        self.worker.process_change_power(**power_info.clone(person_id=person_3_2.id, power_delta=100000).kwargs)

        with self.check_changed(lambda: persons_storage.persons._version):
            with self.check_changed(lambda: places_storage.places._version):
                with mock.patch('the_tale.game.places.attributes.Attributes.freedom', 1):
                    self.worker.sync_data()

        self.assertEqual(self.worker.persons_politic_power, [])
        self.assertEqual(self.worker.places_politic_power, [])

        self.assertTrue(self.p1._modifier.is_NONE)

        self.assertEqual(person_1_1.politic_power.outer_power, 1)
        self.assertEqual(person_2_1.politic_power.outer_power, 100)
        self.assertEqual(person_2_2.politic_power.outer_power, 1000)
        self.assertEqual(person_3_1.politic_power.outer_power, 10000)
        self.assertEqual(person_3_2.politic_power.outer_power, 100000)

        self.assertEqual(self.p1.politic_power.outer_power, 1)
        self.assertEqual(self.p2.politic_power.outer_power, 1100)
        self.assertEqual(self.p3.politic_power.outer_power, 110000)

        self.worker.process_change_power(**power_info.clone(place_id=self.p1.id, power_delta=-10).kwargs)
        self.worker.process_change_power(**power_info.clone(place_id=self.p2.id, power_delta=-1).kwargs)
        self.worker.process_change_power(**power_info.clone(place_id=self.p2.id, power_delta=+10000000).kwargs)
        self.worker.process_change_power(**power_info.clone(place_id=self.p3.id, power_delta=-2).kwargs)
        self.worker.process_change_power(**power_info.clone(place_id=self.p3.id, power_delta=+20).kwargs)

        with self.check_changed(lambda: persons_storage.persons._version):
            with self.check_changed(lambda: places_storage.places._version):
                with mock.patch('the_tale.game.places.attributes.Attributes.freedom', 1):
                    self.worker.sync_data()

        self.assertEqual(self.worker.persons_politic_power, [])
        self.assertEqual(self.worker.places_politic_power, [])

        self.p1 = places_storage.places[self.p1.id]
        self.p2 = places_storage.places[self.p2.id]
        self.p3 = places_storage.places[self.p3.id]

        self.assertEqual(self.p1.politic_power.outer_power, -9.1)
        self.assertEqual(self.p2.politic_power.outer_power, 10000989)
        self.assertEqual(self.p3.politic_power.outer_power, 99018)
