
import smart_imports

smart_imports.all()


class LogicTests(utils_testcase.TestCase):

    def setUp(self):
        super(LogicTests, self).setUp()

        game_logic.create_test_map()

        self.account_1 = self.accounts_factory.create_account()

    def test_remove_expired_access_tokens(self):

        old_created_at = datetime.datetime.now() - datetime.timedelta(minutes=conf.settings.UNPROCESSED_ACCESS_TOKEN_LIVE_TIME)

        t_1 = prototypes.AccessTokenPrototype.fast_create(1, account=None, state=relations.ACCESS_TOKEN_STATE.UNPROCESSED)
        t_1._model.created_at = old_created_at
        t_1.save()

        t_2 = prototypes.AccessTokenPrototype.fast_create(2, account=self.account_1, state=relations.ACCESS_TOKEN_STATE.ACCEPTED)
        t_2._model.created_at = old_created_at
        t_2.save()

        prototypes.AccessTokenPrototype.fast_create(3, account=None, state=relations.ACCESS_TOKEN_STATE.UNPROCESSED)
        prototypes.AccessTokenPrototype.fast_create(4, account=self.account_1, state=relations.ACCESS_TOKEN_STATE.ACCEPTED)

        with self.check_delta(prototypes.AccessTokenPrototype._db_count, -1):
            logic.remove_expired_access_tokens()

        self.assertEqual(prototypes.AccessTokenPrototype.get_by_uid(t_1.uid), None)
