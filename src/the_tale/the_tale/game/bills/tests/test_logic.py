
import smart_imports

smart_imports.all()


class LogicTests(helpers.BaseTestPrototypes):

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

        self.assertEqual(logic.actual_bills_accepted_timestamps(self.account1.id), [utils_logic.to_timestamp(bill.voting_end_at)])

        # second bill

        bill_data = bills.place_change_modifier.PlaceModifier(place_id=self.place1.id,
                                                              modifier_id=places_modifiers.CITY_MODIFIERS.TRADE_CENTER,
                                                              modifier_name=places_modifiers.CITY_MODIFIERS.TRADE_CENTER.text,
                                                              old_modifier_name=None)
        bill_2 = prototypes.BillPrototype.create(self.account2, 'bill-1-caption', bill_data, chronicle_on_accepted='chronicle-on-accepted')

        self.assertEqual(logic.actual_bills_accepted_timestamps(self.account1.id), [utils_logic.to_timestamp(bill.voting_end_at)])

        data = bill_2.user_form_initials
        data['approved'] = True
        form = bill_2.data.get_moderator_form_update(data)

        self.assertTrue(form.is_valid())
        bill_2.update_by_moderator(form)

        bill_2.apply()

        self.assertEqual(logic.actual_bills_accepted_timestamps(self.account1.id), [utils_logic.to_timestamp(bill.voting_end_at)])

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


class ApplyBillsTests(helpers.BaseTestPrototypes):

    @mock.patch('the_tale.game.bills.conf.settings.MIN_VOTES_PERCENT', 0)
    @mock.patch('the_tale.game.bills.conf.settings.BILL_LIVE_TIME', 0)
    def test_stop_bill_without_meaning(self):
        new_name = game_names.generator().get_test_name('new-new-name')

        bill_data_1 = bills_bills.place_renaming.PlaceRenaming(place_id=self.place1.id, name_forms=new_name)
        bill_1 = bills_prototypes.BillPrototype.create(self.account1, 'bill-1-caption', bill_data_1, chronicle_on_accepted='chronicle-on-accepted')
        bill_1.approved_by_moderator = True
        bill_1.save()

        bill_data_2 = bills_bills.place_renaming.PlaceRenaming(place_id=self.place1.id, name_forms=new_name)
        bill_2 = bills_prototypes.BillPrototype.create(self.account1, 'bill-2-caption', bill_data_2, chronicle_on_accepted='chronicle-on-accepted')
        bill_2.approved_by_moderator = True
        bill_2.save()

        logic.apply_bills(logger=mock.Mock())

        bill_1.reload()
        bill_2.reload()

        self.assertTrue(bill_1.state.is_ACCEPTED)
        self.assertTrue(bill_2.state.is_STOPPED)
