# coding: utf-8
import datetime

from the_tale.common.utils.testcase import TestCase

from the_tale.accounts.third_party.conf import third_party_settings

from the_tale.game.logic import create_test_map

from the_tale.accounts.third_party import prototypes
from the_tale.accounts.third_party import relations
from the_tale.accounts.third_party import logic


class LogicTests(TestCase):

    def setUp(self):
        super(LogicTests, self).setUp()

        create_test_map()

        self.account_1 = self.accounts_factory.create_account()

    def test_remove_expired_access_tokens(self):

        old_created_at = datetime.datetime.now() - datetime.timedelta(minutes=third_party_settings.UNPROCESSED_ACCESS_TOKEN_LIVE_TIME)

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
