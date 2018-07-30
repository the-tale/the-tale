
import smart_imports

smart_imports.all()


class RandomPremiumRequestPrototypeTests(utils_testcase.TestCase, personal_messages_helpers.Mixin):

    def setUp(self):
        super(RandomPremiumRequestPrototypeTests, self).setUp()

        game_logic.create_test_map()

        self.account_1 = self.accounts_factory.create_account()
        self.account_2 = self.accounts_factory.create_account()

        prototypes.AccountPrototype._db_all().update(created_at=datetime.datetime.now() - conf.settings.RANDOM_PREMIUM_CREATED_AT_BARRIER)

        self.request = prototypes.RandomPremiumRequestPrototype.create(self.account_1.id, days=30)

        personal_messages_tt_services.personal_messages.cmd_debug_clear_service()

    def test_create(self):
        self.assertEqual(prototypes.RandomPremiumRequestPrototype._db_count(), 1)
        self.assertEqual(self.request.days, 30)
        self.assertEqual(self.request.initiator_id, self.account_1.id)

    def test_get_unprocessed__not_exist(self):
        prototypes.RandomPremiumRequestPrototype._db_all().delete()
        self.assertEqual(prototypes.RandomPremiumRequestPrototype.get_unprocessed(), None)

    def test_get_unprocessed__no_waiting(self):
        prototypes.RandomPremiumRequestPrototype._db_all().update(state=relations.RANDOM_PREMIUM_REQUEST_STATE.PROCESSED)
        self.assertEqual(prototypes.RandomPremiumRequestPrototype.get_unprocessed(), None)

    def test_get_unprocessed__has_waiting(self):
        self.assertEqual(prototypes.RandomPremiumRequestPrototype.get_unprocessed().id, self.request.id)

    def check_not_processed(self, premiums=0):
        self.assertEqual(personal_messages_tt_services.personal_messages.cmd_new_messages_number(self.account_1.id), 0)
        self.assertEqual(prototypes.AccountPrototype._db_filter(premium_end_at__gt=datetime.datetime.now()).count(), premiums)

        self.request.reload()
        self.assertTrue(self.request.state.is_WAITING)
        self.assertEqual(self.request.receiver_id, None)

    def test_process__no_active_accounts(self):
        prototypes.AccountPrototype._db_all().update(active_end_at=datetime.datetime.now())
        self.request.process()
        self.check_not_processed()

    def test_process__only_fast_accounts(self):
        prototypes.AccountPrototype._db_all().update(active_end_at=datetime.datetime.now() + datetime.timedelta(days=1), is_fast=True)
        self.request.process()
        self.check_not_processed()

    def test_process__only_premium_accounts(self):
        prototypes.AccountPrototype._db_all().update(active_end_at=datetime.datetime.now() + datetime.timedelta(days=1),
                                                     premium_end_at=datetime.datetime.now() + datetime.timedelta(days=1))
        self.request.process()
        self.check_not_processed(premiums=2)

    def test_process__only_active_initiator(self):
        prototypes.AccountPrototype._db_all().update(active_end_at=datetime.datetime.now() + datetime.timedelta(days=1))
        self.account_2.remove()
        self.request.process()
        self.check_not_processed()

    def test_process__has_active_accounts(self):
        prototypes.AccountPrototype._db_all().update(active_end_at=datetime.datetime.now() + datetime.timedelta(days=1))

        with self.check_new_message(self.account_2.id, [logic.get_system_user_id()]):
            self.request.process()

        self.assertEqual(list(prototypes.AccountPrototype._db_filter(premium_end_at__gt=datetime.datetime.now()).values_list('id', flat=True)), [self.account_2.id])

        self.request.reload()
        self.assertTrue(self.request.state.is_PROCESSED)
        self.assertEqual(self.request.receiver_id, self.account_2.id)

    def test_process__has_only_new_active_accounts(self):
        prototypes.AccountPrototype._db_all().update(active_end_at=datetime.datetime.now() + datetime.timedelta(days=1),
                                                     created_at=datetime.datetime.now())

        self.request.process()
        self.check_not_processed()
