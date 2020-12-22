
import datetime
import dataclasses

from .. import objects
from .. import relations

from . import helpers


class TokenTests(helpers.BaseTests):

    def test_expired(self):
        now = datetime.datetime.now()

        token = helpers.create_token(666, uid=None, expire_at=now+datetime.timedelta(seconds=100))

        self.assertFalse(token.is_expired(99))
        self.assertTrue(token.is_expired(101))


class AccountInfoTests(helpers.BaseTests):

    def test_remove_private_data(self):
        info = helpers.create_account_info(13)

        self.assertFalse(info.is_removed_by_gdpr())

        self.assertEqual(info.remove_private_data(),
                         objects.AccountInfo(id=13,
                                             name=None,
                                             email=None,
                                             return_url='http://example.com',
                                             state=relations.ACCOUNT_INFO_STATE.REMOVED_BY_GDPR))

        self.assertTrue(info.remove_private_data().is_removed_by_gdpr())

    def test_is_changed(self):
        info = helpers.create_account_info(13)

        self.assertFalse(info.is_changed(info))

        self.assertTrue(dataclasses.replace(info, id=info.id+1).is_changed(info))
        self.assertTrue(dataclasses.replace(info, name=info.name+'x').is_changed(info))
        self.assertTrue(dataclasses.replace(info, email=info.email+'x').is_changed(info))
        self.assertTrue(dataclasses.replace(info, email=info.return_url+'x').is_changed(info))
        self.assertTrue(dataclasses.replace(info, state=relations.ACCOUNT_INFO_STATE.REMOVED_BY_GDPR).is_changed(info))
