# coding: utf-8

import mock
import datetime

from game.bills.prototypes import BillPrototype, VotePrototype
from game.bills.bills import PersonRemove

from game.persons.models import Person, PERSON_STATE

from game.bills.tests.prototype_tests import BaseTestPrototypes


class PersonRemoveTests(BaseTestPrototypes):

    def setUp(self):
        super(PersonRemoveTests, self).setUp()

        self.person1 = sorted(self.place1.persons, key=lambda p: -p.power)[0]
        self.person2 = sorted(self.place2.persons, key=lambda p: -p.power)[-1]

        self.bill_data = PersonRemove(person_id=self.person1.id, old_place_name_forms=self.place1.normalized_name)
        self.bill = BillPrototype.create(self.account1, 'bill-1-caption', 'bill-1-rationale', self.bill_data)


    def test_create(self):
        self.assertEqual(self.bill.data.person_id, self.person1.id)

    def test_actors(self):
        self.assertEqual([id(a) for a in self.bill_data.actors], [id(self.person1.place)])

    def test_update(self):
        form = self.bill.data.get_user_form_update(post={'caption': 'new-caption',
                                                         'rationale': 'new-rationale',
                                                         'person': self.person2.id })
        self.assertTrue(form.is_valid())

        self.bill.update(form)

        self.bill = BillPrototype.get_by_id(self.bill.id)

        self.assertEqual(self.bill.data.person_id, self.person2.id)

    def check_persons_from_place_in_choices(self, place, places_ids, ignored_id):
        persons = sorted(place.persons, key=lambda p: -p.power)

        for person in persons[:len(persons)/2]:
            if person.id == ignored_id:
                continue
            self.assertFalse(person.id in places_ids)

        for person in persons[len(persons)/2:]:
            if person.id == ignored_id:
                continue
            self.assertTrue(person.id in places_ids)


    def test_user_form_choices(self):
        form = self.bill.data.get_user_form_update(initial={'person': self.bill.data.person_id })

        persons_ids = []

        for city_name, person_choices in form.fields['person'].choices:
            persons_ids.extend(choice_id for choice_id, choice_name in person_choices)


        # this statement test situation, when bill is editing after person get alot of power
        # and leave list of persons, whom can be removed
        # it MUST be added to choices
        self.assertTrue(self.bill.data.person_id in persons_ids)

        self.check_persons_from_place_in_choices(self.place1, persons_ids, self.bill.data.person_id)
        self.check_persons_from_place_in_choices(self.place2, persons_ids, self.bill.data.person_id)
        self.check_persons_from_place_in_choices(self.place3, persons_ids, self.bill.data.person_id)


    @mock.patch('game.bills.conf.bills_settings.MIN_VOTES_PERCENT', 0.6)
    @mock.patch('game.bills.prototypes.BillPrototype.time_before_end_step', datetime.timedelta(seconds=0))
    def test_apply(self):
        VotePrototype.create(self.account2, self.bill, False)
        VotePrototype.create(self.account3, self.bill, True)

        form = PersonRemove.ModeratorForm({'approved': True})
        self.assertTrue(form.is_valid())
        self.bill.update_by_moderator(form)

        self.assertTrue(self.bill.apply())

        bill = BillPrototype.get_by_id(self.bill.id)
        self.assertTrue(bill.state._is_ACCEPTED)

        self.assertNotEqual(self.place1.persons[0].id, self.person1.id)
        self.assertTrue(self.person1.out_game)
        self.assertTrue(Person.objects.get(id=self.person1.id).state, PERSON_STATE.OUT_GAME)
