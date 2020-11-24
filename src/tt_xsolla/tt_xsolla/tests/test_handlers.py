
import uuid
import random
import hashlib

from unittest import mock

from aiohttp import test_utils

from tt_protocol.protocol import xsolla_pb2
from tt_protocol.protocol import data_protector_pb2

from tt_web import s11n
from tt_web import utils
from tt_web import postgresql as db

from .. import logic
from .. import protobuf
from .. import operations

from . import helpers


def random_account_info(id=None, name=None, email=None):
    if id is None:
        id = random.randint(1, 100000000)

    if name is None:
        name = uuid.uuid4().hex

    if email is None:
        email = f'{name}@example.com'

    return xsolla_pb2.AccountInfo(id=id,
                                  name=name,
                                  email=email)


class GetTokenTests(helpers.BaseTests):

    async def get_token(self, account_info):
        response = await self.client.post('/get-token',
                                         data=xsolla_pb2.GetTokenRequest(account_info=account_info).SerializeToString())
        data = await self.check_success(response, xsolla_pb2.GetTokenResponse)

        return data

    @test_utils.unittest_run_loop
    async def test_no_token(self):
        account_info = random_account_info()

        data = await self.get_token(account_info)

        stored_token = await operations.load_token(account_info.id)

        self.assertEqual(stored_token.account_id, account_info.id)
        self.assertEqual(stored_token.value, data.token)
        self.assertGreater(stored_token.expire_at, utils.now(helpers.get_config()['custom']['client']['expire_after'] - 1))

        stored_info = await operations.load_account_info(account_info.id)

        self.assertEqual(stored_info, protobuf.to_account_info(account_info))

    @test_utils.unittest_run_loop
    async def test_account_removed_due_gdpr(self):
        info = helpers.create_account_info(123)
        await operations.update_account_info(db.sql, info)

        await logic.delete_account_data(info.id)

        account_info = random_account_info(info.id)

        response = await self.client.post('/get-token',
                                         data=xsolla_pb2.GetTokenRequest(account_info=account_info).SerializeToString())

        await self.check_error(response, 'xsolla.get_token.account_removed_by_gdpr')

        stored_token = await operations.load_token(account_info.id)

        self.assertEqual(stored_token, None)

    @test_utils.unittest_run_loop
    async def test_has_token(self):
        account_info = random_account_info()

        data_1 = await self.get_token(account_info)

        stored_token_1 = await operations.load_token(account_info.id)

        data_2 = await self.get_token(account_info)

        self.assertEqual(data_1, data_2)

        stored_token_2 = await operations.load_token(account_info.id)

        self.assertEqual(stored_token_1, stored_token_2)

        stored_info = await operations.load_account_info(account_info.id)

        self.assertEqual(stored_info, protobuf.to_account_info(account_info))


class XSollaBase(helpers.BaseTests):

    def request_data(self, notification_type, account_info, arguments=None):
        config = helpers.get_config()

        data = {'notification_type': notification_type,
                'settings': {'merchant_id': config['custom']['merchant_id'],
                             'project_id': config['custom']['project_id']},
                'user': {'id': account_info.id,
                         'email': account_info.email,
                         'name': account_info.name}}

        if arguments is not None:
            data |= arguments

        return data

    def headers(self, content):
        h = hashlib.sha1()
        h.update(content.encode('utf-8'))
        h.update(helpers.get_config()['custom']['hooks_key'].encode('utf-8'))

        return {'Authorization': f'Signature {h.hexdigest()}'}

    async def check_xsolla_error(self, response, error, details, status_code=400):
        self.assertEqual(response.status, status_code)

        content = await response.content.read()

        data = s11n.from_json(content)

        self.assertEqual(data['error']['code'], error)
        self.assertEqual(data['error']['details']['code'], details)

    async def check_xsolla_ok(self, response):
        self.assertEqual(response.status, 204)

    async def request_hook(self, request_data):
        content = s11n.to_json(request_data)

        response = await self.client.post('/xsolla-hook',
                                          data=content,
                                          headers=self.headers(content))

        return response

    async def user_validateion_request(self, notification_type='user_validation', account_id=1, save_info=True):
        info = helpers.create_account_info(account_id)

        if save_info:
            await operations.update_account_info(db.sql, info)

        return self.request_data(notification_type, info)

    async def payment_request(self, account_id=1, transaction_id=1, amount=100500):
        info = helpers.create_account_info(account_id)
        await operations.update_account_info(db.sql, info)

        return self.request_data('payment',
                                 info,
                                 arguments={'transaction': {'id': transaction_id},
                                            'purchase': {'virtual_currency': {'quantity': amount}}})

    async def refund_request(self, account_info, transaction_id=1):
        return self.request_data('refund',
                                 account_info,
                                 arguments={'transaction': {'id': transaction_id}})


class XSollaHookTests(XSollaBase):

    @test_utils.unittest_run_loop
    async def test_no_signature(self):
        request_data = await self.user_validateion_request()

        response = await self.client.post('/xsolla-hook',
                                          data=s11n.to_json(request_data))

        await self.check_xsolla_error(response, 'INVALID_SIGNATURE', 'xsolla.hook.signature_has_not_found')

    @test_utils.unittest_run_loop
    async def test_unexpected_signature(self):
        request_data = await self.user_validateion_request()

        response = await self.client.post('/xsolla-hook',
                                          data=s11n.to_json(request_data),
                                          headers={'Authorization': 'Signature: blablabla'})

        await self.check_xsolla_error(response, 'INVALID_SIGNATURE', 'xsolla.hook.unexpected_signature')

    @test_utils.unittest_run_loop
    async def test_no_settings(self):
        request_data = await self.user_validateion_request()

        del request_data['settings']

        response = await self.request_hook(request_data)

        await self.check_xsolla_error(response, 'INVALID_PARAMETER', 'xsolla.hook.no_settings_info')

    @test_utils.unittest_run_loop
    async def test_no_merchant_id(self):
        request_data = await self.user_validateion_request()

        del request_data['settings']['merchant_id']

        response = await self.request_hook(request_data)

        await self.check_xsolla_error(response, 'INVALID_PARAMETER', 'xsolla.hook.wrong_merchant_id')

    @test_utils.unittest_run_loop
    async def test_no_project_id(self):
        request_data = await self.user_validateion_request()

        del request_data['settings']['project_id']

        response = await self.request_hook(request_data)

        await self.check_xsolla_error(response, 'INVALID_PARAMETER', 'xsolla.hook.wrong_project_id')

    @test_utils.unittest_run_loop
    async def test_unsupported_notification_type(self):
        request_data = await self.user_validateion_request(notification_type='wrong_notification_id')

        response = await self.request_hook(request_data)

        await self.check_xsolla_error(response, 'INVALID_PARAMETER', 'xsolla.hook.unknown_notification_type')

    @test_utils.unittest_run_loop
    async def test_unknown_error(self):
        request_data = await self.user_validateion_request()

        async def validate_user(*argv, **kwargs):
            raise Exception('some test exception')

        with mock.patch('tt_xsolla.logic.validate_user', validate_user):
            response = await self.request_hook(request_data)

        await self.check_xsolla_error(response, 'api.unknown_error', 'api.unknown_error', status_code=500)

    @test_utils.unittest_run_loop
    async def test_success(self):
        request_data = await self.user_validateion_request()

        response = await self.request_hook(request_data)

        await self.check_xsolla_ok(response)


class XSollaHookUserValidationTests(XSollaBase):

    @test_utils.unittest_run_loop
    async def test_success(self):
        request_data = await self.user_validateion_request()

        response = await self.request_hook(request_data)

        await self.check_xsolla_ok(response)

    @test_utils.unittest_run_loop
    async def test_no_user(self):
        request_data = await self.user_validateion_request(save_info=False)

        response = await self.request_hook(request_data)

        await self.check_xsolla_error(response,
                                      'INVALID_USER',
                                      'xsolla.hook.user_validation.account_not_found',
                                      status_code=400)

    @test_utils.unittest_run_loop
    async def test_wrong_account_id_format(self):
        request_data = await self.user_validateion_request(account_id='wrong_id', save_info=False)

        response = await self.request_hook(request_data)

        await self.check_xsolla_error(response,
                                      'INVALID_USER',
                                      'xsolla.hook.user_validation.wrong_account_id_format',
                                      status_code=400)


class XSollaHookPaymentTests(XSollaBase):

    @test_utils.unittest_run_loop
    async def test_success(self):
        request_data = await self.payment_request(transaction_id=1)
        response = await self.request_hook(request_data)
        await self.check_xsolla_ok(response)

    @test_utils.unittest_run_loop
    async def test_multiple_tries(self):
        request_data = await self.payment_request(transaction_id=1)

        for i in range(3):
            response = await self.request_hook(request_data)
            await self.check_xsolla_ok(response)

    @test_utils.unittest_run_loop
    async def test_multiple_invoices(self):
        for transaction_id in range(3, 8):
            request_data = await self.payment_request(transaction_id=transaction_id)

            for i in range(3):
                response = await self.request_hook(request_data)
                await self.check_xsolla_ok(response)

    @test_utils.unittest_run_loop
    async def test_changed_data(self):
        request_data = await self.payment_request(account_id=1, transaction_id=1)
        response = await self.request_hook(request_data)
        await self.check_xsolla_ok(response)

        request_data = await self.payment_request(account_id=2, transaction_id=1)
        response = await self.request_hook(request_data)

        await self.check_xsolla_error(response,
                                      'xsolla.hook.payment.can_not_register_invoice',
                                      'xsolla.hook.payment.can_not_register_invoice',
                                      status_code=400)


class XSollaHookRefundTests(XSollaBase):

    async def prepair_account(self):
        info = helpers.create_account_info(666)
        await operations.update_account_info(db.sql, info)
        return info

    async def prepair_invoice(self, account_id):
        invoice = helpers.create_invoice(1, account_id=account_id)

        is_registered = await logic.register_invoice(invoice)
        self.assertTrue(is_registered)

        return invoice

    @test_utils.unittest_run_loop
    async def test_success(self):
        info = await self.prepair_account()
        invoice = await self.prepair_invoice(info.id)

        request_data = await self.refund_request(info, transaction_id=invoice.xsolla_id)
        response = await self.request_hook(request_data)
        await self.check_xsolla_ok(response)

    @test_utils.unittest_run_loop
    async def test_multiple_tries(self):
        info = await self.prepair_account()
        invoice = await self.prepair_invoice(info.id)

        request_data = await self.refund_request(info, transaction_id=invoice.xsolla_id)

        response = await self.request_hook(request_data)
        await self.check_xsolla_ok(response)

        response = await self.request_hook(request_data)
        await self.check_xsolla_ok(response)


class DataProtectionCollectDataTests(helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test_wrong_secret(self):
        secret = 'wrong.secret'

        request = await self.client.post('/data-protection-collect-data',
                                         data=data_protector_pb2.PluginReportRequest(account_id='777',
                                                                                     secret=secret).SerializeToString())
        await self.check_error(request, 'xsolla.data_protection_collect_data.wrong_secret')

    @test_utils.unittest_run_loop
    async def test_no_data(self):
        secret = helpers.get_config()['custom']['data_protector']['secret']

        request = await self.client.post('/data-protection-collect-data',
                                         data=data_protector_pb2.PluginReportRequest(account_id='777',
                                                                                     secret=secret).SerializeToString())
        response = await self.check_success(request, data_protector_pb2.PluginReportResponse, raw=True)

        self.assertEqual(response.result, data_protector_pb2.PluginReportResponse.ResultType.Value('SUCCESS'))

        report = s11n.from_json(response.data)

        self.assertEqual(report, [])

    async def prepair_info(self, account_id):
        info = helpers.create_account_info(account_id)
        await operations.update_account_info(db.sql, info)
        return info

    async def prepair_invoice(self, account_id, xsolla_id, amount):
        invoice = helpers.create_invoice(xsolla_id, account_id=account_id, amount=amount)

        result = await logic.register_invoice(invoice)

        self.assertTrue(result.is_ok())

        return await operations.load_invoice(xsolla_id)

    async def prepair_complex_data(self):
        info_1 = await self.prepair_info(666)
        info_2 = await self.prepair_info(777)

        invoice_1 = await self.prepair_invoice(info_1.id, 10001, 1000500)
        invoice_2 = await self.prepair_invoice(info_2.id, 10002, 1000600)
        invoice_3 = await self.prepair_invoice(info_1.id, 10003, 1000700)

        return [info_1, info_2], [invoice_1, invoice_2, invoice_3]

    @test_utils.unittest_run_loop
    async def test_has_data(self):
        infos, invoices = await self.prepair_complex_data()

        secret = helpers.get_config()['custom']['data_protector']['secret']

        request = await self.client.post('/data-protection-collect-data',
                                         data=data_protector_pb2.PluginReportRequest(account_id=str(infos[0].id),
                                                                                     secret=secret).SerializeToString())
        response = await self.check_success(request, data_protector_pb2.PluginReportResponse, raw=True)

        self.assertEqual(response.result, data_protector_pb2.PluginReportResponse.ResultType.Value('SUCCESS'))

        report = s11n.from_json(response.data)

        self.assertCountEqual(report,
                              [['account_info', {'email': infos[0].email,
                                                 'name': infos[0].name}],
                               ['invoice', {'purchased_amount': invoices[0].purchased_amount,
                                            'xsolla_id': invoices[0].xsolla_id}],
                               ['invoice', {'purchased_amount': invoices[2].purchased_amount,
                                            'xsolla_id': invoices[2].xsolla_id}]])


class DataProtectionDeleteDataTests(helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test_wrong_secret(self):
        secret = 'wrong.secret'

        request = await self.client.post('/data-protection-delete-data',
                                         data=data_protector_pb2.PluginDeletionRequest(account_id='777',
                                                                                       secret=secret).SerializeToString())
        await self.check_error(request, 'xsolla.data_protection_delete_data.wrong_secret')

    @test_utils.unittest_run_loop
    async def test_no_data(self):
        secret = helpers.get_config()['custom']['data_protector']['secret']

        request = await self.client.post('/data-protection-delete-data',
                                         data=data_protector_pb2.PluginDeletionRequest(account_id='777',
                                                                                       secret=secret).SerializeToString())
        response = await self.check_success(request, data_protector_pb2.PluginDeletionResponse, raw=True)

        self.assertEqual(response.result, data_protector_pb2.PluginDeletionResponse.ResultType.Value('SUCCESS'))

    async def prepair_info(self, account_id):
        info = helpers.create_account_info(account_id)
        await operations.update_account_info(db.sql, info)
        return info

    async def prepair_invoice(self, account_id, xsolla_id, amount):
        invoice = helpers.create_invoice(xsolla_id, account_id=account_id, amount=amount)

        result = await logic.register_invoice(invoice)

        self.assertTrue(result.is_ok())

        return await operations.load_invoice(xsolla_id)

    async def prepair_complex_data(self):
        info_1 = await self.prepair_info(666)
        info_2 = await self.prepair_info(777)

        invoice_1 = await self.prepair_invoice(info_1.id, 10001, 1000500)
        invoice_2 = await self.prepair_invoice(info_2.id, 10002, 1000600)
        invoice_3 = await self.prepair_invoice(info_1.id, 10003, 1000700)

        return [info_1, info_2], [invoice_1, invoice_2, invoice_3]

    @test_utils.unittest_run_loop
    async def test_has_data(self):
        infos, invoices = await self.prepair_complex_data()

        secret = helpers.get_config()['custom']['data_protector']['secret']

        request = await self.client.post('/data-protection-delete-data',
                                         data=data_protector_pb2.PluginDeletionRequest(account_id=str(infos[0].id),
                                                                                       secret=secret).SerializeToString())
        response = await self.check_success(request, data_protector_pb2.PluginDeletionResponse, raw=True)

        self.assertEqual(response.result, data_protector_pb2.PluginDeletionResponse.ResultType.Value('SUCCESS'))

        data = await logic.get_data_report(infos[0].id)

        self.assertCountEqual(data,
                              [('account_info', {'email': None,
                                                 'name': None}),
                               ('invoice', {'purchased_amount': invoices[0].purchased_amount,
                                            'xsolla_id': invoices[0].xsolla_id}),
                               ('invoice', {'purchased_amount': invoices[2].purchased_amount,
                                            'xsolla_id': invoices[2].xsolla_id})])
