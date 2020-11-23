
# ATTENTION: Due xsolla does not allow api access withoud secret api key (and other information),
#            we can not test api intergration on regular basis.
#            To test api, you need to setup next environment variables:
#            XSOLLA_TEST_MERCHANT_ID
#            XSOLLA_TEST_PROJECT_ID
#            XSOLLA_TEST_API_KEY


import os
import logging

from aiohttp import test_utils

from .. import xsolla

from . import helpers


class RealClientTests(helpers.BaseTests):

    def get_test_config(self):
        return {'merchant_id': os.environ.get('XSOLLA_TEST_MERCHANT_ID'),
                'project_id': os.environ.get('XSOLLA_TEST_PROJECT_ID'),
                'api_key': os.environ.get('XSOLLA_TEST_API_KEY'),
                'test_account_id': os.environ.get('XSOLLA_TEST_ACCOUNT_ID')}

    def get_xsolla_client(self):
        config = self.get_test_config()

        return xsolla.RealClient(config={'merchant_id': config['merchant_id'],
                                         'project_id': config['project_id'],
                                         'api_key': config['api_key'],
                                         'expire_after': 24*60*60,
                                         'mode': 'sandbox'})

    @test_utils.unittest_run_loop
    async def test_request_token(self):
        if not all(self.get_test_config().values()):
            return

        client = self.get_xsolla_client()

        account_info = helpers.create_account_info(uid=1)

        token = await client.request_token(account_info, logging)

        print(token)
