
import smart_imports

smart_imports.all()


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
