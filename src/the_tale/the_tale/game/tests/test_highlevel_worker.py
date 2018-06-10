
from unittest import mock

from the_tale.amqp_environment import environment

from the_tale.common.utils import testcase

from the_tale.game import names

from the_tale.game.bills import bills
from the_tale.game.bills import prototypes as bills_prototypes

from the_tale.game.persons import storage as persons_storage
from the_tale.game.persons import logic as persons_logic
from the_tale.game.persons.models import Person

from the_tale.game.places import storage as places_storage
from the_tale.game.places import logic as places_logic

from ..balance import constants as c
from ..logic import create_test_map
from .. import turn
from ..bills.conf import bills_settings
from ..logic_storage import LogicStorage
from .. import tt_api_impacts

from the_tale.game.politic_power import logic as politic_power_logic
from the_tale.game.politic_power import storage as politic_power_storage


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
        self.worker.process_initialize(turn.number(), 'highlevel')

    def test_process_initialize(self):
        self.assertTrue(self.worker.initialized)
        self.assertEqual(self.worker.worker_id, 'highlevel')
        self.assertEqual(self.worker.turn_number, 0)

    @mock.patch('the_tale.game.workers.highlevel.Worker.sync_data', fake_sync_data)
    @mock.patch('the_tale.game.workers.highlevel.Worker.apply_bills', fake_apply_bills)
    @mock.patch('subprocess.call', lambda x: None)
    @mock.patch('the_tale.game.balance.constants.MAP_SYNC_TIME', 10)
    def test_process_next_turn(self):

        turn.increment()

        self.assertEqual(turn.number(), 1)

        for i in range(c.MAP_SYNC_TIME-1):
            self.worker.process_next_turn(turn.number())
            self.assertFalse(hasattr(self.worker, '_data_synced'))

            if turn.number() < bills_settings.BILLS_PROCESS_INTERVAL / c.TURN_DELTA:
                self.assertFalse(hasattr(self.worker, '_bills_applied'))
            else:
                self.assertEqual(self.worker._bills_applied, turn.number() // (bills_settings.BILLS_PROCESS_INTERVAL // c.TURN_DELTA))

            turn.increment()

        self.worker.process_next_turn(turn.number())
        self.assertTrue(self.worker._data_synced)

    @mock.patch('the_tale.game.bills.conf.bills_settings.MIN_VOTES_PERCENT', 0)
    @mock.patch('the_tale.game.bills.conf.bills_settings.BILL_LIVE_TIME', 0)
    def test_apply_bills__stop_bill_without_meaning(self):
        from the_tale.forum.models import Category, SubCategory

        forum_category = Category.objects.create(caption='category-1', slug='category-1')
        SubCategory.objects.create(caption=bills_settings.FORUM_CATEGORY_UID + '-caption',
                                   uid=bills_settings.FORUM_CATEGORY_UID,
                                   category=forum_category)

        new_name = names.generator().get_test_name('new-new-name')

        bill_data_1 = bills.PlaceRenaming(place_id=self.p1.id, name_forms=new_name)
        bill_1 = bills_prototypes.BillPrototype.create(self.account, 'bill-1-caption', bill_data_1, chronicle_on_accepted='chronicle-on-accepted')
        bill_1.approved_by_moderator = True
        bill_1.save()

        bill_data_2 = bills.PlaceRenaming(place_id=self.p1.id, name_forms=new_name)
        bill_2 = bills_prototypes.BillPrototype.create(self.account, 'bill-2-caption', bill_data_2, chronicle_on_accepted='chronicle-on-accepted')
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

        with mock.patch('the_tale.game.places.attributes.Attributes.set_power_economic', set_power_economic), \
             mock.patch('the_tale.game.places.attributes.Attributes.sync_size', sync_size), \
             mock.patch('the_tale.game.places.objects.Place.effects', mock.Mock(update_step=update_step, effects=[], serialize=lambda: {})), \
             mock.patch('the_tale.game.places.objects.Place.sync_habits', sync_habits), \
             mock.patch('the_tale.game.places.objects.Place.refresh_attributes', refresh_attributes), \
             mock.patch('the_tale.game.places.objects.Place.mark_as_updated', mark_as_updated):
            self.worker.sync_data()

        places_number = len(places_storage.places.all())

        self.assertEqual(set_power_economic.call_count, places_number)
        self.assertEqual(sync_size.call_count, places_number)
        self.assertEqual(sync_habits.call_count, places_number)
        self.assertEqual(refresh_attributes.call_count, places_number)
        self.assertEqual(mark_as_updated.call_count, places_number)

    def give_power_to_person(self, person, power, fame):
        impacts = persons_logic.tt_power_impacts(person_inner_circle=False,
                                                 place_inner_circle=False,
                                                 actor_type=tt_api_impacts.OBJECT_TYPE.HERO,
                                                 actor_id=666,
                                                 person=person,
                                                 amount=power,
                                                 fame=fame)

        politic_power_logic.add_power_impacts(impacts)

    def give_power_to_place(self, place, power, fame):
        impacts = places_logic.tt_power_impacts(inner_circle=False,
                                                actor_type=tt_api_impacts.OBJECT_TYPE.HERO,
                                                actor_id=666,
                                                place=place,
                                                amount=power,
                                                fame=fame)
        politic_power_logic.add_power_impacts(impacts)

    @mock.patch('the_tale.game.persons.attributes.Attributes.places_help_amount', 1)
    @mock.patch('the_tale.game.places.attributes.Attributes.freedom', 1)
    @mock.patch('the_tale.game.balance.constants.PLACE_POWER_REDUCE_FRACTION', 0.9)
    @mock.patch('the_tale.game.places.objects.Place.refresh_attributes', mock.Mock())
    def test_sync_data(self):
        tt_api_impacts.debug_clear_service()

        self.assertEqual(politic_power_storage.places.outer_power(self.p1.id), 0)
        self.assertEqual(politic_power_storage.places.inner_power(self.p1.id), 0)
        self.assertEqual(politic_power_storage.places.outer_power(self.p2.id), 0)
        self.assertEqual(politic_power_storage.places.inner_power(self.p2.id), 0)
        self.assertEqual(politic_power_storage.places.outer_power(self.p3.id), 0)
        self.assertEqual(politic_power_storage.places.inner_power(self.p3.id), 0)

        self.assertEqual(Person.objects.filter(place_id=self.p1.id).count(), 3)
        self.assertEqual(Person.objects.filter(place_id=self.p2.id).count(), 3)
        self.assertEqual(Person.objects.filter(place_id=self.p3.id).count(), 3)
        self.assertEqual(len(persons_storage.persons.all()), 9)

        popularity = places_logic.get_hero_popularity(666)

        self.assertEqual(popularity.get_fame(self.p1.id), 0)
        self.assertEqual(popularity.get_fame(self.p2.id), 0)
        self.assertEqual(popularity.get_fame(self.p3.id), 0)

        person_1_1 = self.p1.persons[0]
        person_2_1, person_2_2 = self.p2.persons[0:2]
        person_3_1, person_3_2 = self.p3.persons[0:2]

        self.give_power_to_person(person=person_1_1, power=1, fame=2)
        self.give_power_to_person(person=person_2_1, power=100, fame=200)
        self.give_power_to_person(person=person_2_2, power=1000, fame=2000)
        self.give_power_to_person(person=person_3_1, power=10000, fame=20000)
        self.give_power_to_person(person=person_3_2, power=100000, fame=200000)

        with self.check_changed(lambda: persons_storage.persons._version):
            with self.check_changed(lambda: places_storage.places._version):
                self.worker.sync_data()

        self.assertTrue(self.p1._modifier.is_NONE)

        turn.increment()

        self.assertEqual(politic_power_storage.persons.outer_power(person_1_1.id), 0)
        self.assertEqual(politic_power_storage.persons.outer_power(person_2_1.id), 90)
        self.assertEqual(politic_power_storage.persons.outer_power(person_2_2.id), 900)
        self.assertEqual(politic_power_storage.persons.outer_power(person_3_1.id), 9000)
        self.assertEqual(politic_power_storage.persons.outer_power(person_3_2.id), 90000)

        self.assertEqual(politic_power_storage.places.outer_power(self.p1.id), 0)
        self.assertEqual(politic_power_storage.places.outer_power(self.p2.id), 990)
        self.assertEqual(politic_power_storage.places.outer_power(self.p3.id), 99000)

        popularity = places_logic.get_hero_popularity(666)

        self.assertEqual(popularity.get_fame(self.p1.id), 1)
        self.assertEqual(popularity.get_fame(self.p2.id), 2189)
        self.assertEqual(popularity.get_fame(self.p3.id), 218997)

        self.give_power_to_place(place=self.p1, power=-10, fame=-20)
        self.give_power_to_place(place=self.p2, power=-1, fame=-2)
        self.give_power_to_place(place=self.p2, power=+10000000, fame=20000000)
        self.give_power_to_place(place=self.p3, power=-2, fame=-40)
        self.give_power_to_place(place=self.p3, power=+20, fame=40)

        with self.check_changed(lambda: persons_storage.persons._version):
            with self.check_changed(lambda: places_storage.places._version):
                self.worker.sync_data()

        self.p1 = places_storage.places[self.p1.id]
        self.p2 = places_storage.places[self.p2.id]
        self.p3 = places_storage.places[self.p3.id]

        self.assertEqual(politic_power_storage.places.outer_power(self.p1.id), -9)
        self.assertEqual(politic_power_storage.places.outer_power(self.p2.id), 9000890)
        self.assertEqual(politic_power_storage.places.outer_power(self.p3.id), 89116)

        popularity = places_logic.get_hero_popularity(666)

        self.assertEqual(popularity.get_fame(self.p1.id), 0)
        self.assertEqual(popularity.get_fame(self.p2.id), 19911015)
        self.assertEqual(popularity.get_fame(self.p3.id), 218038)
