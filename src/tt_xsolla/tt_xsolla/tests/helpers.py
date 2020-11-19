
import os
import uuid
import datetime

from tt_web import utils
from tt_web.tests import helpers as web_helpers

from .. import service
from .. import objects
from .. import operations
from .. import relations


class BaseTests(web_helpers.BaseTests):

    def create_application(self):
        return service.create_application(get_config())

    async def clean_environment(self, app=None):
        await operations.clean_database()


def get_config():
    config_path = os.path.join(os.path.dirname(__file__), 'fixtures', 'config.json')
    return utils.load_config(config_path)


def create_account_info(uid, version=1):
    return objects.AccountInfo(id=uid,
                               name=f'name-{uid}-{version}',
                               email=f'email-{uid}-{version}@example.com',
                               state=relations.ACCOUNT_INFO_STATE.ACTIVE)


def create_token(account_id, uid=None, expire_at=None):
    if uid is None:
        uid = uuid.uuid4().hex

    if expire_at is None:
        expire_at = datetime.datetime.now() + datetime.timedelta(hours=1)

    return objects.Token(value=uid,
                         account_id=account_id,
                         expire_at=expire_at)


def create_invoice(xsolla_id, account_id, amount=666, is_test=False, is_fake=False):
    return objects.Invoice(xsolla_id=xsolla_id,
                           account_id=account_id,
                           purchased_amount=amount,
                           is_test=is_test,
                           is_fake=is_fake)
