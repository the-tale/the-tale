# coding: utf-8
import mock
import datetime

from contextlib import contextmanager

from the_tale.linguistics.tests import helpers as linguistics_helpers

from the_tale.game import names

from the_tale.game.relations import RACE

from the_tale.game.bills.prototypes import BillPrototype
from the_tale.game.bills import bills
from the_tale.game.bills import relations as bills_relations
from the_tale.game.bills.tests.test_prototype import BaseTestPrototypes

from the_tale.game.chronicle.models import Record, RECORD_TYPE

from the_tale.game.map.places.prototypes import BuildingPrototype
from the_tale.game.map.places.modifiers import TradeCenter, CraftCenter

from the_tale.game.chronicle import prototypes

@contextmanager
def check_record_created(self, record_type, records_number=1):
    old_records_number = Record.objects.all().count()

    yield

    self.assertEqual(old_records_number + records_number, Record.objects.all().count())
    self.assertEqual(Record.objects.all().order_by('-id')[0].type, record_type)

@mock.patch('the_tale.game.bills.prototypes.BillPrototype.time_before_voting_end', datetime.timedelta(seconds=0))
def process_bill(bill, success):
    with mock.patch('the_tale.game.bills.prototypes.BillPrototype.is_percents_barier_not_passed', not success):
        bill.apply()

class BillPlaceRenamingTests(BaseTestPrototypes):

    def setUp(self):
        super(BillPlaceRenamingTests, self).setUp()

        bill_data = bills.PlaceRenaming(place_id=self.place1.id, name_forms=names.generator.get_test_name('new-name'))
        self.bill = BillPrototype.create(self.account1, 'bill-caption', 'bill-rationale', bill_data, chronicle_on_accepted='chronicle-on-accepted')

        data = linguistics_helpers.get_word_post_data(bill_data.name_forms, prefix='name')
        data.update({'approved': True})
        self.form = bills.PlaceRenaming.ModeratorForm(data)
        self.assertTrue(self.form.is_valid())

    def test_bill_successed(self):
        self.bill.update_by_moderator(self.form)
        with check_record_created(self, RECORD_TYPE.PLACE_CHANGE_NAME_BILL_SUCCESSED):
            process_bill(self.bill, True)
        self.assertEqual(prototypes.RecordPrototype._db_latest().text, 'chronicle-on-accepted')


class BillPlaceDescriptionTests(BaseTestPrototypes):

    def setUp(self):
        super(BillPlaceDescriptionTests, self).setUp()

        bill_data = bills.PlaceDescripton(place_id=self.place1.id, description='new description')
        self.bill = BillPrototype.create(self.account1, 'bill-1-caption', 'bill-1-rationale', bill_data, chronicle_on_accepted='chronicle-on-accepted')

        self.form = bills.PlaceDescripton.ModeratorForm({'approved': True})
        self.assertTrue(self.form.is_valid())

    def test_bill_successed(self):
        self.bill.update_by_moderator(self.form)
        with check_record_created(self, RECORD_TYPE.PLACE_CHANGE_DESCRIPTION_BILL_SUCCESSED):
            process_bill(self.bill, True)
        self.assertEqual(prototypes.RecordPrototype._db_latest().text, 'chronicle-on-accepted')


class BillPlaceChangeModifierTests(BaseTestPrototypes):

    def setUp(self):
        super(BillPlaceChangeModifierTests, self).setUp()

        bill_data = bills.PlaceModifier(place_id=self.place1.id, modifier_id=TradeCenter.get_id(), modifier_name=TradeCenter.TYPE.text, old_modifier_name=None)
        self.bill = BillPrototype.create(self.account1, 'bill-1-caption', 'bill-1-rationale', bill_data, chronicle_on_accepted='chronicle-on-accepted')

        self.form = bills.PlaceModifier.ModeratorForm({'approved': True})
        self.assertTrue(self.form.is_valid())

    def test_bill_successed(self):
        self.bill.update_by_moderator(self.form)
        with check_record_created(self, RECORD_TYPE.PLACE_CHANGE_MODIFIER_BILL_SUCCESSED):
            process_bill(self.bill, True)
        self.assertEqual(prototypes.RecordPrototype._db_latest().text, 'chronicle-on-accepted')


class BillPlaceExchangeResourcesTests(BaseTestPrototypes):

    def setUp(self):
        from the_tale.game.bills.tests.helpers import choose_exchange_resources
        from the_tale.game.bills.bills import PlaceResourceExchange

        super(BillPlaceExchangeResourcesTests, self).setUp()

        self.resource_1, self.resource_2 = choose_exchange_resources()

        self.bill_data = PlaceResourceExchange(place_1_id=self.place1.id,
                                               place_2_id=self.place2.id,
                                               resource_1=self.resource_1,
                                               resource_2=self.resource_2)

        self.bill = BillPrototype.create(self.account1, 'bill-1-caption', 'bill-1-rationale', self.bill_data, chronicle_on_accepted='chronicle-on-accepted', chronicle_on_ended='chronicle-on-ended')

        self.form = bills.PlaceModifier.ModeratorForm({'approved': True})
        self.assertTrue(self.form.is_valid())


    def test_bill_successed(self):
        self.bill.update_by_moderator(self.form)
        with check_record_created(self, RECORD_TYPE.PLACE_RESOURCE_EXCHANGE_BILL_SUCCESSED):
            process_bill(self.bill, True)

        self.assertEqual(prototypes.RecordPrototype._db_latest().text, 'chronicle-on-accepted')


    def test_bill_ended(self):
        self.bill.update_by_moderator(self.form)
        process_bill(self.bill, True)

        with check_record_created(self, RECORD_TYPE.PLACE_RESOURCE_EXCHANGE_BILL_ENDED):
            self.bill.end()

        self.assertEqual(prototypes.RecordPrototype._db_latest().text, 'chronicle-on-ended')


class BillPlaceConversionResourcesTests(BaseTestPrototypes):

    def setUp(self):
        from the_tale.game.bills.tests.helpers import choose_conversions
        from the_tale.game.bills.bills import PlaceResourceConversion

        super(BillPlaceConversionResourcesTests, self).setUp()

        self.conversion_1, self.conversion_2 = choose_conversions()

        self.bill_data = PlaceResourceConversion(place_id=self.place1.id,
                                                 conversion=self.conversion_1)

        self.bill = BillPrototype.create(self.account1, 'bill-1-caption', 'bill-1-rationale', self.bill_data, chronicle_on_accepted='chronicle-on-accepted', chronicle_on_ended='chronicle-on-ended')

        self.form = bills.PlaceModifier.ModeratorForm({'approved': True})
        self.assertTrue(self.form.is_valid())


    def test_bill_successed(self):
        self.bill.update_by_moderator(self.form)
        with check_record_created(self, RECORD_TYPE.PLACE_RESOURCE_CONVERSION_BILL_SUCCESSED):
            process_bill(self.bill, True)
        self.assertEqual(prototypes.RecordPrototype._db_latest().text, 'chronicle-on-accepted')

    def test_bill_ended(self):
        self.bill.update_by_moderator(self.form)
        process_bill(self.bill, True)

        with check_record_created(self, RECORD_TYPE.PLACE_RESOURCE_CONVERSION_BILL_ENDED):
            self.bill.end()
        self.assertEqual(prototypes.RecordPrototype._db_latest().text, 'chronicle-on-ended')


class BillPersonRemoveTests(BaseTestPrototypes):

    def setUp(self):
        super(BillPersonRemoveTests, self).setUp()

        bill_data = bills.PersonRemove(person_id=self.place1.persons[0].id, old_place_name_forms=self.place1.utg_name)
        self.bill = BillPrototype.create(self.account1, 'bill-1-caption', 'bill-1-rationale', bill_data, chronicle_on_accepted='chronicle-on-accepted')

        self.form = bills.PersonRemove.ModeratorForm({'approved': True})
        self.assertTrue(self.form.is_valid())

    @mock.patch('the_tale.game.chronicle.records.PlaceChangeRace.create_record', lambda x: None)
    @mock.patch('the_tale.game.chronicle.records.PersonArrivedToPlace.create_record', lambda x: None)
    def test_bill_successed(self):
        self.bill.update_by_moderator(self.form)
        with check_record_created(self, RECORD_TYPE.PERSON_REMOVE_BILL_SUCCESSED):
            process_bill(self.bill, True)
        self.assertEqual(prototypes.RecordPrototype._db_latest().text, 'chronicle-on-accepted')


class BillBuildingCreateTests(BaseTestPrototypes):

    def setUp(self):
        super(BillBuildingCreateTests, self).setUp()

        bill_data = bills.BuildingCreate(person_id=self.place1.persons[0].id,
                                         old_place_name_forms=self.place1.utg_name,
                                         utg_name=names.generator.get_test_name('building-name'))
        self.bill = BillPrototype.create(self.account1, 'bill-1-caption', 'bill-1-rationale', bill_data, chronicle_on_accepted='chronicle-on-accepted')

        data = linguistics_helpers.get_word_post_data(bill_data.building_name_forms, prefix='name')
        data.update({'approved': True})

        self.form = bills.BuildingCreate.ModeratorForm(data)
        self.assertTrue(self.form.is_valid())


    def test_bill_successed(self):
        self.bill.update_by_moderator(self.form)
        with check_record_created(self, RECORD_TYPE.BUILDING_CREATE_BILL_SUCCESSED):
            process_bill(self.bill, True)
        self.assertEqual(prototypes.RecordPrototype._db_latest().text, 'chronicle-on-accepted')


class BillBuildingDestroyTests(BaseTestPrototypes):

    def setUp(self):
        super(BillBuildingDestroyTests, self).setUp()

        self.person = self.place1.persons[0]
        self.building = BuildingPrototype.create(self.person, utg_name=names.generator.get_test_name('building-name'))

        bill_data = bills.BuildingDestroy(person_id=self.person.id, old_place_name_forms=self.place1.utg_name)
        self.bill = BillPrototype.create(self.account1, 'bill-1-caption', 'bill-1-rationale', bill_data, chronicle_on_accepted='chronicle-on-accepted')

        self.form = bills.BuildingDestroy.ModeratorForm({'approved': True})
        self.assertTrue(self.form.is_valid())

    def test_bill_successed(self):
        self.bill.update_by_moderator(self.form)
        with check_record_created(self, RECORD_TYPE.BUILDING_DESTROY_BILL_SUCCESSED):
            process_bill(self.bill, True)
        self.assertEqual(prototypes.RecordPrototype._db_latest().text, 'chronicle-on-accepted')

class BillBuildingRenamingTests(BaseTestPrototypes):

    def setUp(self):
        super(BillBuildingRenamingTests, self).setUp()

        self.person = self.place1.persons[0]
        self.building = BuildingPrototype.create(self.person, utg_name=names.generator.get_test_name('building-name'))

        bill_data = bills.BuildingRenaming(person_id=self.person.id,
                                           old_place_name_forms=self.place1.utg_name,
                                           new_building_name_forms=names.generator.get_test_name('new-building-name'))
        self.bill = BillPrototype.create(self.account1, 'bill-1-caption', 'bill-1-rationale', bill_data, chronicle_on_accepted='chronicle-on-accepted')

        data = linguistics_helpers.get_word_post_data(bill_data.new_building_name_forms, prefix='name')
        data.update({'approved': True})


        self.form = bills.BuildingRenaming.ModeratorForm(data)
        self.assertTrue(self.form.is_valid())

    def test_bill_successed(self):
        self.bill.update_by_moderator(self.form)
        with check_record_created(self, RECORD_TYPE.BUILDING_RENAMING_BILL_SUCCESSED):
            process_bill(self.bill, True)
        self.assertEqual(prototypes.RecordPrototype._db_latest().text, 'chronicle-on-accepted')


class PlaceLosedModifierTests(BaseTestPrototypes):

    def setUp(self):
        super(PlaceLosedModifierTests, self).setUp()

        self.place1.modifier = CraftCenter.get_id()
        self.place1.save()

    @mock.patch('the_tale.game.map.places.modifiers.prototypes.CraftCenter.is_enough_power', False)
    def test_reset_modifier(self):
        with check_record_created(self, RECORD_TYPE.PLACE_LOSED_MODIFIER):
            self.place1.sync_modifier()


class PersonMovementsTests(BaseTestPrototypes):

    def setUp(self):
        super(PersonMovementsTests, self).setUp()

    @mock.patch('the_tale.game.persons.prototypes.PersonPrototype.is_stable', False)
    @mock.patch('the_tale.game.map.places.prototypes.PlacePrototype.max_persons_number', 0)
    def test_person_left(self):
        with mock.patch('the_tale.game.map.places.races.Races.dominant_race', self.place1.race):
            with check_record_created(self, RECORD_TYPE.PERSON_LEFT_PLACE, records_number=len(self.place1.persons)):
                self.place1.sync_persons(force_add=True)

    @mock.patch('the_tale.game.chronicle.records.PlaceChangeRace.create_record', lambda x: None)
    def test_person_arrived(self):
        with check_record_created(self, RECORD_TYPE.PERSON_ARRIVED_TO_PLACE):
            with mock.patch('the_tale.game.map.places.prototypes.PlacePrototype.max_persons_number', len(self.place1.persons) + 1):
                self.place1.sync_persons(force_add=True)


class PlaceChangeRace(BaseTestPrototypes):

    def setUp(self):
        super(PlaceChangeRace, self).setUp()

        for race_id in RACE.records:
            if self.place1.race != race_id:
                self.next_race_id = race_id

    def test_place_race_changed(self):
        self.place1.races._races[self.next_race_id] = 99999

        with check_record_created(self, RECORD_TYPE.PLACE_CHANGE_RACE):
            self.place1.sync_race()



class BillPersonChronicleTests(BaseTestPrototypes):

    def setUp(self):
        super(BillPersonChronicleTests, self).setUp()

        bill_data = bills.PersonChronicle(person_id=self.place1.persons[0].id, old_place_name_forms=self.place1.utg_name, power_bonus=bills_relations.POWER_BONUS_CHANGES.DOWN)
        self.bill = BillPrototype.create(self.account1, 'bill-1-caption', 'bill-1-rationale', bill_data, chronicle_on_accepted='chronicle-on-accepted')

        self.form = bills.PersonChronicle.ModeratorForm({'approved': True})
        self.assertTrue(self.form.is_valid())

    @mock.patch('the_tale.game.chronicle.records.PlaceChangeRace.create_record', lambda x: None)
    @mock.patch('the_tale.game.chronicle.records.PersonArrivedToPlace.create_record', lambda x: None)
    def test_bill_successed(self):
        self.bill.update_by_moderator(self.form)
        with check_record_created(self, RECORD_TYPE.PERSON_CHRONICLE_BILL_SUCCESSED):
            process_bill(self.bill, True)
        self.assertEqual(prototypes.RecordPrototype._db_latest().text, 'chronicle-on-accepted')


class BillPlaceChronicleTests(BaseTestPrototypes):

    def setUp(self):
        super(BillPlaceChronicleTests, self).setUp()

        bill_data = bills.PlaceChronicle(place_id=self.place1.id, old_name_forms=self.place1.utg_name, power_bonus=bills_relations.POWER_BONUS_CHANGES.DOWN)
        self.bill = BillPrototype.create(self.account1, 'bill-1-caption', 'bill-1-rationale', bill_data, chronicle_on_accepted='chronicle-on-accepted')

        self.form = bills.PersonChronicle.ModeratorForm({'approved': True})
        self.assertTrue(self.form.is_valid())

    @mock.patch('the_tale.game.chronicle.records.PlaceChangeRace.create_record', lambda x: None)
    @mock.patch('the_tale.game.chronicle.records.PersonArrivedToPlace.create_record', lambda x: None)
    def test_bill_successed(self):
        self.bill.update_by_moderator(self.form)
        with check_record_created(self, RECORD_TYPE.PLACE_CHRONICLE_BILL_SUCCESSED):
            process_bill(self.bill, True)
        self.assertEqual(prototypes.RecordPrototype._db_latest().text, 'chronicle-on-accepted')
