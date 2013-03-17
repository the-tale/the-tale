# coding: utf-8

import mock
import datetime

from game.map.places.models import Building
from game.map.places.prototypes import BuildingPrototype
from game.map.places.storage import buildings_storage

from game.bills.relations import BILL_STATE
from game.bills.prototypes import BillPrototype, VotePrototype
from game.bills.bills import BuildingDestroy
from game.bills.tests.prototype_tests import BaseTestPrototypes


class BuildingDestroyTests(BaseTestPrototypes):

    def setUp(self):
        super(BuildingDestroyTests, self).setUp()

        self.person_1 = self.place1.persons[0]
        self.person_2 = self.place2.persons[0]
        self.person_3 = self.place3.persons[0]

        self.building_1 = BuildingPrototype.create(self.person_1)
        self.building_2 = BuildingPrototype.create(self.person_2)

        bill_data = BuildingDestroy(person_id=self.person_1.id, old_place_name_forms=self.place1.normalized_name)
        self.bill = BillPrototype.create(self.account1, 'bill-1-caption', 'bill-1-rationale', bill_data)


    def test_create(self):
        self.assertEqual(self.bill.data.person_id, self.person_1.id)

    def test_update(self):
        form = self.bill.data.get_user_form_update(post={'caption': 'new-caption',
                                                         'rationale': 'new-rationale',
                                                         'person': self.person_2.id })
        self.assertTrue(form.is_valid())

        self.bill.update(form)

        self.bill = BillPrototype.get_by_id(self.bill.id)

        self.assertEqual(self.bill.data.person_id, self.person_2.id)


    def test_user_form_choices(self):
        form = self.bill.data.get_user_form_update(initial={'person': self.bill.data.person_id })

        persons_ids = []

        for city_name, person_choices in form.fields['person'].choices:
            persons_ids.extend(choice_id for choice_id, choice_name in person_choices)

        self.assertEqual(set(persons_ids), set([self.person_1.id, self.person_2.id]))


    @mock.patch('game.bills.conf.bills_settings.MIN_VOTES_NUMBER', 2)
    @mock.patch('game.bills.conf.bills_settings.MIN_VOTES_PERCENT', 0.6)
    @mock.patch('game.bills.prototypes.BillPrototype.time_before_end_step', datetime.timedelta(seconds=0))
    def test_apply(self):
        self.assertEqual(Building.objects.all().count(), 2)

        VotePrototype.create(self.account2, self.bill, False)
        VotePrototype.create(self.account3, self.bill, True)

        form = BuildingDestroy.ModeratorForm({'approved': True})
        self.assertTrue(form.is_valid())
        self.bill.update_by_moderator(form)

        self.assertTrue(self.bill.apply())

        bill = BillPrototype.get_by_id(self.bill.id)
        self.assertTrue(bill.state._is_ACCEPTED)

        self.assertEqual(Building.objects.all().count(), 1)

        building = buildings_storage.all()[0]

        self.assertEqual(building.person.id, self.person_2.id)
        self.assertEqual(building.place.id, self.place2.id)


    @mock.patch('game.bills.conf.bills_settings.MIN_VOTES_NUMBER', 2)
    @mock.patch('game.bills.conf.bills_settings.MIN_VOTES_PERCENT', 0.6)
    @mock.patch('game.bills.prototypes.BillPrototype.time_before_end_step', datetime.timedelta(seconds=0))
    def test_duplicate_apply(self):
        self.assertEqual(Building.objects.all().count(), 2)

        VotePrototype.create(self.account2, self.bill, False)
        VotePrototype.create(self.account3, self.bill, True)

        form = BuildingDestroy.ModeratorForm({'approved': True})
        self.assertTrue(form.is_valid())
        self.bill.update_by_moderator(form)
        self.assertTrue(self.bill.apply())

        bill = BillPrototype.get_by_id(self.bill.id)
        bill.state = BILL_STATE.VOTING
        bill.save()

        self.assertTrue(bill.apply())

        self.assertEqual(Building.objects.all().count(), 1)
