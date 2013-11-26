# coding: utf-8

import mock
import datetime

from dext.utils import s11n

from textgen.words import Noun

from the_tale.game.map.places.models import Building
from the_tale.game.map.places.prototypes import BuildingPrototype
from the_tale.game.map.places.relations import BUILDING_STATE

from the_tale.game.bills.prototypes import BillPrototype, VotePrototype
from the_tale.game.bills.bills import BuildingRenaming
from the_tale.game.bills.tests.prototype_tests import BaseTestPrototypes


class BuildingRenamingTests(BaseTestPrototypes):

    def setUp(self):
        super(BuildingRenamingTests, self).setUp()

        self.person_1 = self.place1.persons[0]
        self.person_2 = self.place2.persons[0]
        self.person_3 = self.place3.persons[0]

        self.building = BuildingPrototype.create(self.person_1, name_forms=Noun.fast_construct('building-name'))
        self.building_2 = BuildingPrototype.create(self.person_2, name_forms=Noun.fast_construct('building-name-2'))

        self.bill_data = BuildingRenaming(person_id=self.person_1.id,
                                          old_place_name_forms=self.place1.normalized_name,
                                          new_building_name_forms=Noun.fast_construct('new-building-name'))
        self.bill = BillPrototype.create(self.account1, 'bill-caption', 'bill-rationale', self.bill_data)


    def test_create(self):
        self.assertEqual(self.bill.data.person_id, self.person_1.id)
        self.assertEqual(self.bill.data.old_name, 'building-name')
        self.assertEqual(self.bill.data.new_name, 'new-building-name')

    def test_actors(self):
        self.assertEqual([id(a) for a in self.bill_data.actors], [id(self.person_1.place)])

    def test_update(self):
        form = self.bill.data.get_user_form_update(post={'caption': 'new-caption',
                                                         'rationale': 'new-rationale',
                                                         'person': self.person_2.id,
                                                         'new_name': 'new-building-name-2'})
        self.assertTrue(form.is_valid())

        self.bill.update(form)

        self.bill = BillPrototype.get_by_id(self.bill.id)

        self.assertEqual(self.bill.data.person_id, self.person_2.id)
        self.assertEqual(self.bill.data.old_name, 'building-name-2')
        self.assertEqual(self.bill.data.new_name, 'new-building-name-2')

    def test_user_form_choices(self):
        form = self.bill.data.get_user_form_update(initial={'person': self.bill.data.person_id })

        persons_ids = []

        for city_name, person_choices in form.fields['person'].choices:
            persons_ids.extend(choice_id for choice_id, choice_name in person_choices)

        self.assertEqual(set(persons_ids), set([self.person_1.id, self.person_2.id]))


    @mock.patch('the_tale.game.bills.conf.bills_settings.MIN_VOTES_PERCENT', 0.6)
    @mock.patch('the_tale.game.bills.prototypes.BillPrototype.time_before_voting_end', datetime.timedelta(seconds=0))
    def test_apply(self):
        VotePrototype.create(self.account2, self.bill, False)
        VotePrototype.create(self.account3, self.bill, True)

        noun = Noun.fast_construct('r-building-name')

        form = BuildingRenaming.ModeratorForm({'approved': True,
                                               'new_building_name_forms': s11n.to_json(noun.serialize())})
        self.assertTrue(form.is_valid())
        self.bill.update_by_moderator(form)

        self.assertTrue(self.bill.apply())

        bill = BillPrototype.get_by_id(self.bill.id)
        self.assertTrue(bill.state.is_ACCEPTED)

        self.assertEqual(Building.objects.filter(state=BUILDING_STATE.WORKING).count(), 2)

        self.building.reload()

        self.assertEqual(self.building.name, 'r-building-name')

    @mock.patch('the_tale.game.bills.conf.bills_settings.MIN_VOTES_PERCENT', 0.6)
    @mock.patch('the_tale.game.bills.prototypes.BillPrototype.time_before_voting_end', datetime.timedelta(seconds=0))
    def test_no_building(self):

        VotePrototype.create(self.account2, self.bill, False)
        VotePrototype.create(self.account3, self.bill, True)

        noun = Noun.fast_construct('r-building-name')

        form = BuildingRenaming.ModeratorForm({'approved': True,
                                               'new_building_name_forms': s11n.to_json(noun.serialize())})
        self.assertTrue(form.is_valid())
        self.bill.update_by_moderator(form)

        self.building.destroy()
        self.building.save()

        self.assertTrue(self.bill.apply())

        self.assertEqual(Building.objects.filter(state=BUILDING_STATE.WORKING).count(), 1)

        self.building.reload()
        self.assertEqual(self.building.name, 'building-name')
