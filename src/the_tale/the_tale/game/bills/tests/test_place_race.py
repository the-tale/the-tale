# coding: utf-8

from unittest import mock
import datetime

from the_tale.game import relations as game_relations

from the_tale.game.bills.prototypes import BillPrototype, VotePrototype
from the_tale.game.bills.bills import PlaceRace

from the_tale.game.bills import relations

from the_tale.game.bills.tests.helpers import BaseTestPrototypes

from the_tale.game.places import logic as places_logic


class PlaceRaceTests(BaseTestPrototypes):

    def setUp(self):
        super(PlaceRaceTests, self).setUp()

        self.place = self.place1
        self.place_2 = self.place2

        self.place.race = game_relations.RACE.ORC
        self.place_2.race = game_relations.RACE.ELF

        self.bill_data = PlaceRace(place_id=self.place.id,
                                   new_race=game_relations.RACE.GOBLIN,
                                   old_race=self.place.race)

        self.bill = BillPrototype.create(self.account1, 'bill-1-caption', 'bill-1-rationale', self.bill_data, chronicle_on_accepted='chronicle-on-accepted')

    def test_create(self):
        self.assertEqual(self.bill.data.place_id, self.place.id)
        self.assertTrue(self.bill.data.new_race.is_GOBLIN)
        self.assertTrue(self.bill.data.old_race.is_ORC)

    def test_actors(self):
        self.assertEqual([id(a) for a in self.bill_data.actors], [id(self.place)])

    @mock.patch('the_tale.game.persons.objects.Person.race', game_relations.RACE.DWARF)
    def test_update(self):
        form = self.bill.data.get_user_form_update(post={'caption': 'new-caption',
                                                         'rationale': 'new-rationale',
                                                         'place': self.place_2.id,
                                                         'chronicle_on_accepted': 'chronicle-on-accepted',
                                                         'new_race': game_relations.RACE.DWARF})
        self.assertTrue(form.is_valid())

        self.bill.update(form)

        self.bill = BillPrototype.get_by_id(self.bill.id)

        self.assertEqual(self.bill.data.place_id, self.place_2.id)
        self.assertTrue(self.bill.data.new_race.is_DWARF)
        self.assertTrue(self.bill.data.old_race.is_ELF)

    @mock.patch('the_tale.game.persons.objects.Person.race', game_relations.RACE.DWARF)
    def test_success_form_validation(self):
        form = self.bill.data.get_user_form_update(post={'caption': 'new-caption',
                                                         'rationale': 'new-rationale',
                                                         'chronicle_on_accepted': 'chronicle-on-accepted-2',
                                                         'place': self.place_2.id,
                                                         'new_race': game_relations.RACE.DWARF})
        self.assertTrue(form.is_valid())


    @mock.patch('the_tale.game.persons.objects.Person.race', game_relations.RACE.GOBLIN)
    def test_not_allowed_race(self):
        form = self.bill.data.get_user_form_update(post={'caption': 'new-caption',
                                                         'rationale': 'new-rationale',
                                                         'chronicle_on_accepted': 'chronicle-on-accepted-2',
                                                         'place': self.place_2.id,
                                                         'new_race': game_relations.RACE.ELF})
        self.assertFalse(form.is_valid())


    @mock.patch('the_tale.game.persons.objects.Person.race', game_relations.RACE.GOBLIN)
    @mock.patch('the_tale.game.bills.conf.bills_settings.MIN_VOTES_PERCENT', 0.6)
    @mock.patch('the_tale.game.bills.prototypes.BillPrototype.time_before_voting_end', datetime.timedelta(seconds=0))
    def test_apply(self):
        VotePrototype.create(self.account2, self.bill, relations.VOTE_TYPE.AGAINST)
        VotePrototype.create(self.account3, self.bill, relations.VOTE_TYPE.FOR)

        data = self.bill.user_form_initials
        data['approved'] = True
        form = self.bill.data.get_moderator_form_update(data)

        self.assertTrue(form.is_valid())
        self.bill.update_by_moderator(form)

        self.assertTrue(self.bill.apply())

        bill = BillPrototype.get_by_id(self.bill.id)
        self.assertTrue(bill.state.is_ACCEPTED)

        self.assertTrue(self.place.race.is_GOBLIN)


    @mock.patch('the_tale.game.persons.objects.Person.race', game_relations.RACE.GOBLIN)
    @mock.patch('the_tale.game.bills.conf.bills_settings.MIN_VOTES_PERCENT', 0.6)
    @mock.patch('the_tale.game.bills.prototypes.BillPrototype.time_before_voting_end', datetime.timedelta(seconds=0))
    def test_has_meaning__duplicate_race(self):
        VotePrototype.create(self.account2, self.bill, relations.VOTE_TYPE.AGAINST)
        VotePrototype.create(self.account3, self.bill, relations.VOTE_TYPE.FOR)

        data = self.bill.user_form_initials
        data['approved'] = True
        form = self.bill.data.get_moderator_form_update(data)

        self.assertTrue(form.is_valid())
        self.bill.update_by_moderator(form)

        self.bill.data.place.race = self.bill.data.new_race

        places_logic.save_place(self.bill.data.place)

        self.assertFalse(self.bill.has_meaning())



    @mock.patch('the_tale.game.bills.conf.bills_settings.MIN_VOTES_PERCENT', 0.6)
    @mock.patch('the_tale.game.bills.prototypes.BillPrototype.time_before_voting_end', datetime.timedelta(seconds=0))
    def test_has_meaning__no_master_with_race(self):
        with mock.patch('the_tale.game.persons.objects.Person.race', game_relations.RACE.GOBLIN):
            VotePrototype.create(self.account2, self.bill, relations.VOTE_TYPE.AGAINST)
            VotePrototype.create(self.account3, self.bill, relations.VOTE_TYPE.FOR)

            data = self.bill.user_form_initials
            data['approved'] = True
            form = self.bill.data.get_moderator_form_update(data)

            self.assertTrue(form.is_valid())
            self.bill.update_by_moderator(form)

        self.bill.data.place.race = self.bill.data.new_race

        places_logic.save_place(self.bill.data.place)

        with mock.patch('the_tale.game.persons.objects.Person.race', game_relations.RACE.ELF):
            self.assertFalse(self.bill.has_meaning())
