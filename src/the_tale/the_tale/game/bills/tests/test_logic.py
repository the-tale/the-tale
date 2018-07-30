
import smart_imports

smart_imports.all()


class LogicTests(helpers.BaseTestPrototypes):

    def setUp(self):
        super(LogicTests, self).setUp()

    @mock.patch('the_tale.game.bills.conf.settings.MIN_VOTES_PERCENT', 0.6)
    @mock.patch('the_tale.game.bills.prototypes.BillPrototype.time_before_voting_end', datetime.timedelta(seconds=0))
    def test_actual_bills_accepted_timestamps(self):
        self.assertEqual(logic.actual_bills_accepted_timestamps(self.account1.id), [])

        bill_data = bills.place_change_modifier.PlaceModifier(place_id=self.place1.id,
                                                              modifier_id=places_modifiers.CITY_MODIFIERS.TRADE_CENTER,
                                                              modifier_name=places_modifiers.CITY_MODIFIERS.TRADE_CENTER.text,
                                                              old_modifier_name=None)
        bill = prototypes.BillPrototype.create(self.account1, 'bill-1-caption', bill_data, chronicle_on_accepted='chronicle-on-accepted')

        self.assertEqual(logic.actual_bills_accepted_timestamps(self.account1.id), [])

        data = bill.user_form_initials
        data['approved'] = True
        form = bill.data.get_moderator_form_update(data)

        self.assertTrue(form.is_valid())
        bill.update_by_moderator(form)

        bill.apply()

        self.assertEqual(logic.actual_bills_accepted_timestamps(self.account1.id), [time.mktime(bill.voting_end_at.timetuple())])

        # second bill

        bill_data = bills.place_change_modifier.PlaceModifier(place_id=self.place1.id,
                                                              modifier_id=places_modifiers.CITY_MODIFIERS.TRADE_CENTER,
                                                              modifier_name=places_modifiers.CITY_MODIFIERS.TRADE_CENTER.text,
                                                              old_modifier_name=None)
        bill_2 = prototypes.BillPrototype.create(self.account2, 'bill-1-caption', bill_data, chronicle_on_accepted='chronicle-on-accepted')

        self.assertEqual(logic.actual_bills_accepted_timestamps(self.account1.id), [time.mktime(bill.voting_end_at.timetuple())])

        data = bill_2.user_form_initials
        data['approved'] = True
        form = bill_2.data.get_moderator_form_update(data)

        self.assertTrue(form.is_valid())
        bill_2.update_by_moderator(form)

        bill_2.apply()

        self.assertEqual(logic.actual_bills_accepted_timestamps(self.account1.id), [time.mktime(bill.voting_end_at.timetuple())])

        # third bill

        bill_data = bills.place_change_modifier.PlaceModifier(place_id=self.place1.id,
                                                              modifier_id=places_modifiers.CITY_MODIFIERS.TRADE_CENTER,
                                                              modifier_name=places_modifiers.CITY_MODIFIERS.TRADE_CENTER.text,
                                                              old_modifier_name=None)
        bill_3 = prototypes.BillPrototype.create(self.account1, 'bill-1-caption', bill_data, chronicle_on_accepted='chronicle-on-accepted')

        self.assertEqual(logic.actual_bills_accepted_timestamps(self.account1.id), [time.mktime(bill.voting_end_at.timetuple())])

        data = bill_3.user_form_initials
        data['approved'] = True
        form = bill_3.data.get_moderator_form_update(data)

        self.assertTrue(form.is_valid())
        bill_3.update_by_moderator(form)

        bill_3.apply()

        self.assertCountEqual(logic.actual_bills_accepted_timestamps(self.account1.id),
                              [time.mktime(bill.voting_end_at.timetuple()), time.mktime(bill_3.voting_end_at.timetuple())])
