
import datetime
import dataclasses
import asyncio

from unittest import mock

from aiohttp import test_utils

from tt_web import postgresql as db

from .. import logic
from .. import xsolla
from .. import objects
from .. import operations

from . import helpers


class FindTokenTests(helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test_no_account_info(self):
        info = helpers.create_account_info(1)

        found_token = await logic.find_token(info, expiration_delta=0)

        self.assertTrue(found_token.is_error('AccountInfoNotFound'))

    @test_utils.unittest_run_loop
    async def test_account_info_removed_by_gdpr(self):
        info = helpers.create_account_info(1)

        await operations.update_account_info(db.sql, info)

        await logic.delete_account_data(info.id)

        loaded_info = await operations.load_account_info(info.id)

        found_token = await logic.find_token(loaded_info, expiration_delta=0)

        self.assertTrue(found_token.is_error('AccountRemovedByGDPR'))

    @test_utils.unittest_run_loop
    async def test_account_info_changed(self):
        old_info = helpers.create_account_info(1)
        new_info = helpers.create_account_info(1, version=2)

        await operations.update_account_info(db.sql, old_info)

        found_token = await logic.find_token(new_info, expiration_delta=0)

        self.assertTrue(found_token.is_error('AccountInfoChanged'))

    @test_utils.unittest_run_loop
    async def test_no_token(self):
        info = helpers.create_account_info(1)

        await operations.update_account_info(db.sql, info)

        found_token = await logic.find_token(info, expiration_delta=0)

        self.assertTrue(found_token.is_error('TokenNotFound'))

    @test_utils.unittest_run_loop
    async def test_token_expired(self):
        info = helpers.create_account_info(1)
        token = helpers.create_token(info.id, expire_at=datetime.datetime.now() + datetime.timedelta(seconds=10))

        await operations.sync_token_with_account_info(token, info)

        found_token = await logic.find_token(info, expiration_delta=10)

        self.assertTrue(found_token.is_error('TokenExpired'))

        found_token = await logic.find_token(info, expiration_delta=0)

        self.assertTrue(found_token.is_ok())

    @test_utils.unittest_run_loop
    async def test_token_found(self):
        info = helpers.create_account_info(1)
        token = helpers.create_token(info.id)

        await operations.sync_token_with_account_info(token, info)

        found_token = await logic.find_token(info, expiration_delta=10)

        self.assertTrue(found_token.is_ok())

        self.assertEqual(found_token.value, token)


class RequestTokenTests(helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test(self):
        info = helpers.create_account_info(1)
        client = xsolla.get_client(helpers.get_config()['custom'], 'normal')

        token = await logic.request_token(info, client, logger=mock.Mock())

        found_token = await logic.find_token(info, expiration_delta=10)
        self.assertEqual(token, found_token)

        found_info = await operations.load_account_info(info.id)
        self.assertEqual(info, found_info)


class ValidateUserTests(helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test(self):
        info = helpers.create_account_info(1)
        await operations.update_account_info(db.sql, info)

        is_valid = await logic.validate_user(info.id)
        self.assertTrue(is_valid)

        is_valid = await logic.validate_user(info.id+1)
        self.assertFalse(is_valid)

    @test_utils.unittest_run_loop
    async def test_data_removed_due_gdpr(self):
        info = helpers.create_account_info(1)
        await operations.update_account_info(db.sql, info)

        await logic.delete_account_data(info.id)

        is_valid = await logic.validate_user(info.id)
        self.assertFalse(is_valid)

    @test_utils.unittest_run_loop
    async def test_two_infos(self):
        info_1 = helpers.create_account_info(1)
        info_2 = helpers.create_account_info(2)

        await operations.update_account_info(db.sql, info_1)
        await operations.update_account_info(db.sql, info_2)

        is_valid = await logic.validate_user(info_1.id)
        self.assertTrue(is_valid)

        is_valid = await logic.validate_user(info_2.id)
        self.assertTrue(is_valid)


class RegisterInvoiceTests(helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test_no_account_info(self):
        invoice = helpers.create_invoice(1, 666)

        with self.check_event_setupped(False):
            result = await logic.register_invoice(invoice)

        self.assertTrue(result.is_error('NoAccountForInvoice'))

        stored_invoice = await operations.load_cancelation(1)
        self.assertEqual(stored_invoice, None)

    @test_utils.unittest_run_loop
    async def test_new_invoice(self):
        info = helpers.create_account_info(666)
        await operations.update_account_info(db.sql, info)

        invoice = helpers.create_invoice(info.id, 666)

        with self.check_event_setupped(True):
            result = await logic.register_invoice(invoice)

        self.assertTrue(result.is_ok())

        stored_invoice = await operations.load_invoice(invoice.xsolla_id)
        self.assertEqual(stored_invoice, invoice)

    @test_utils.unittest_run_loop
    async def test_repeated_invoices(self):
        info_1 = helpers.create_account_info(666)
        await operations.update_account_info(db.sql, info_1)

        info_2 = helpers.create_account_info(667)
        await operations.update_account_info(db.sql, info_2)

        invoice = helpers.create_invoice(1, info_1.id)

        with self.check_event_setupped(True):
            result = await logic.register_invoice(invoice)

        self.assertTrue(result.is_ok())

        with self.check_event_setupped(True):
            result = await logic.register_invoice(invoice)

        self.assertTrue(result.is_ok())

        with self.check_event_setupped(False):
            result = await logic.register_invoice(dataclasses.replace(invoice, account_id=info_2.id))

        self.assertTrue(result.is_error('InvoiceDataDoesNotEqualToStored'))

        with self.check_event_setupped(False):
            result = await logic.register_invoice(dataclasses.replace(invoice, purchased_amount=invoice.purchased_amount+1))

        self.assertTrue(result.is_error('InvoiceDataDoesNotEqualToStored'))

        stored_invoice = await operations.load_invoice(invoice.xsolla_id)
        self.assertEqual(stored_invoice, invoice)


class RegisterCancellationTests(helpers.BaseTests):

    async def prepair_invoice(self):
        info = helpers.create_account_info(666)
        await operations.update_account_info(db.sql, info)

        invoice = helpers.create_invoice(1, info.id)

        result = await logic.register_invoice(invoice)
        self.assertTrue(result.is_ok())

        return invoice

    @test_utils.unittest_run_loop
    async def test_no_invoice(self):
        invoice = await self.prepair_invoice()

        result = await logic.register_cancellation(invoice.xsolla_id+1)
        self.assertTrue(result.is_error('NoInvoiceToCancel'))

        stored_cancelation = await operations.load_cancelation(invoice.xsolla_id+1)
        self.assertEqual(stored_cancelation, None)

    @test_utils.unittest_run_loop
    async def test_new_cancelation(self):
        invoice = await self.prepair_invoice()

        result = await logic.register_cancellation(invoice.xsolla_id)
        self.assertTrue(result.is_ok())

        stored_cancelation = await operations.load_cancelation(invoice.xsolla_id)
        self.assertEqual(stored_cancelation,
                         objects.Cancellation(account_id=invoice.account_id,
                                              xsolla_id=invoice.xsolla_id))

    @test_utils.unittest_run_loop
    async def test_repeated_cancelations(self):
        invoice = await self.prepair_invoice()

        for i in range(2):
            result = await logic.register_cancellation(invoice.xsolla_id)
            self.assertTrue(result.is_ok())

        stored_cancelation = await operations.load_cancelation(invoice.xsolla_id)
        self.assertEqual(stored_cancelation,
                         objects.Cancellation(account_id=invoice.account_id,
                                              xsolla_id=invoice.xsolla_id))


class ProcessInvoiceTests(helpers.BaseTests):

    async def prepair_invoice(self, account_id, xsolla_id, is_test=False):
        info = helpers.create_account_info(account_id)
        await operations.update_account_info(db.sql, info)

        invoice = helpers.create_invoice(xsolla_id, account_id=info.id, is_test=is_test)

        result = await logic.register_invoice(invoice)
        self.assertTrue(result.is_ok())

        return await operations.load_invoice(xsolla_id)

    @test_utils.unittest_run_loop
    async def test_no_invoice(self):
        processor = mock.Mock(return_value=True)

        result = await logic.process_invoice(config=helpers.get_config(),
                                             processor=processor,
                                             logger=mock.Mock())

        self.assertFalse(result)

    @test_utils.unittest_run_loop
    async def test_error_while_processing(self):
        target_invoice = await self.prepair_invoice(100, 1000)

        async def processor(invoice, config, logger):
            self.assertEqual(target_invoice, invoice)
            raise Exception('!')

        result = await logic.process_invoice(config=helpers.get_config(),
                                             processor=processor,
                                             logger=mock.Mock())

        self.assertFalse(result)

        results = await db.sql('SELECT * FROM invoices WHERE xsolla_id=%(xsolla_id)s', {'xsolla_id': target_invoice.xsolla_id})
        self.assertEqual(results[0]['processed_at'], None)

    @test_utils.unittest_run_loop
    async def test_can_not_process(self):
        target_invoice = await self.prepair_invoice(100, 1000)

        async def processor(invoice, config, logger):
            self.assertEqual(target_invoice, invoice)
            return False

        result = await logic.process_invoice(config=helpers.get_config(),
                                             processor=processor,
                                             logger=mock.Mock())

        self.assertTrue(result)

        results = await db.sql('SELECT * FROM invoices WHERE xsolla_id=%(xsolla_id)s', {'xsolla_id': target_invoice.xsolla_id})
        self.assertEqual(results[0]['processed_at'], None)

    @test_utils.unittest_run_loop
    async def test_success(self):
        target_invoice = await self.prepair_invoice(100, 1000)

        async def processor(invoice, config, logger):
            self.assertEqual(target_invoice, invoice)
            return True

        result = await logic.process_invoice(config=helpers.get_config(),
                                             processor=processor,
                                             logger=mock.Mock())
        self.assertTrue(result)

        results = await db.sql('SELECT * FROM invoices WHERE xsolla_id=%(xsolla_id)s', {'xsolla_id': target_invoice.xsolla_id})
        self.assertNotEqual(results[0]['processed_at'], None)

    @test_utils.unittest_run_loop
    async def test_test_invoice(self):
        target_invoice = await self.prepair_invoice(100, 1000, is_test=True)

        async def processor(invoice, config, logger):
            # must not be called
            raise Exception('!')

        result = await logic.process_invoice(config=helpers.get_config(),
                                             processor=processor,
                                             logger=mock.Mock())
        self.assertTrue(result)

        results = await db.sql('SELECT * FROM invoices WHERE xsolla_id=%(xsolla_id)s', {'xsolla_id': target_invoice.xsolla_id})
        self.assertNotEqual(results[0]['processed_at'], None)

    @test_utils.unittest_run_loop
    async def test_concurrent_processing(self):
        invoice_1 = await self.prepair_invoice(100, 1000)
        invoice_2 = await self.prepair_invoice(101, 1001)

        calls = []

        async def processor(invoice, config, logger):
            calls.append(invoice.xsolla_id)
            return True

        tasks = []

        for i in range(10):
            tasks.append(logic.process_invoice(config=helpers.get_config(),
                                               processor=processor,
                                               logger=mock.Mock()))
        await asyncio.gather(*tasks)

        self.assertCountEqual(calls, [invoice_1.xsolla_id, invoice_2.xsolla_id])

        results = await db.sql('SELECT * FROM invoices')

        self.assertEqual(len(results), 2)

        self.assertNotEqual(results[0]['processed_at'], None)
        self.assertNotEqual(results[1]['processed_at'], None)


class GetAndDeleteDataTests(helpers.BaseTests):

    async def prepair_info(self, account_id):
        info = helpers.create_account_info(account_id)
        await operations.update_account_info(db.sql, info)
        return info

    async def prepair_invoice(self, account_id, xsolla_id, amount):
        invoice = helpers.create_invoice(xsolla_id, account_id=account_id, amount=amount)

        result = await logic.register_invoice(invoice)

        self.assertTrue(result.is_ok())

        return await operations.load_invoice(xsolla_id)

    @test_utils.unittest_run_loop
    async def test_no_data(self):
        data = await logic.get_data_report(666)
        self.assertEqual(data, [])

        await logic.delete_account_data(666)

    @test_utils.unittest_run_loop
    async def test_only_account_info(self):
        info = await self.prepair_info(666)

        data = await logic.get_data_report(666)
        self.assertEqual(data, [('account_info', {'email': info.email,
                                                  'name': info.name})])

    async def prepair_complex_data(self):
        info_1 = await self.prepair_info(666)
        info_2 = await self.prepair_info(777)

        invoice_1 = await self.prepair_invoice(info_1.id, 10001, 1000500)
        invoice_2 = await self.prepair_invoice(info_2.id, 10002, 1000600)
        invoice_3 = await self.prepair_invoice(info_1.id, 10003, 1000700)

        return [info_1, info_2], [invoice_1, invoice_2, invoice_3]

    @test_utils.unittest_run_loop
    async def test_complex_data(self):
        infos, invoices = await self.prepair_complex_data()

        data = await logic.get_data_report(infos[0].id)

        self.assertCountEqual(data,
                              [('account_info', {'email': infos[0].email,
                                                 'name': infos[0].name}),
                               ('invoice', {'purchased_amount': invoices[0].purchased_amount,
                                            'xsolla_id': invoices[0].xsolla_id}),
                               ('invoice', {'purchased_amount': invoices[2].purchased_amount,
                                            'xsolla_id': invoices[2].xsolla_id})])

    @test_utils.unittest_run_loop
    async def test_removed_data(self):
        infos, invoices = await self.prepair_complex_data()

        await logic.delete_account_data(infos[0].id)

        data = await logic.get_data_report(infos[0].id)

        self.assertCountEqual(data,
                              [('account_info', {'email': None,
                                                 'name': None}),
                               ('invoice', {'purchased_amount': invoices[0].purchased_amount,
                                            'xsolla_id': invoices[0].xsolla_id}),
                               ('invoice', {'purchased_amount': invoices[2].purchased_amount,
                                            'xsolla_id': invoices[2].xsolla_id})])

        data = await logic.get_data_report(infos[1].id)

        self.assertCountEqual(data,
                              [('account_info', {'email': infos[1].email,
                                                 'name': infos[1].name}),
                               ('invoice', {'purchased_amount': invoices[1].purchased_amount,
                                            'xsolla_id': invoices[1].xsolla_id})])


class InvoiceFromXsollaDataTests(helpers.BaseTests):

    def test_normal(self):
        invoice = logic.invoice_from_xsolla_data({'transaction': {'id': 666},
                                                  'user': {'id': 13},
                                                  'purchase': {'virtual_currency': {'quantity': 100500}}})
        self.assertEqual(invoice, objects.Invoice(xsolla_id=666,
                                                  account_id=13,
                                                  purchased_amount=100500,
                                                  is_test=False,
                                                  is_fake=False))

    def test_is_fake(self):
        invoice = logic.invoice_from_xsolla_data({'transaction': {'id': 666},
                                                  'user': {'id': 13},
                                                  'purchase': {'virtual_currency': {'quantity': 100500}}}, is_fake=True)
        self.assertEqual(invoice, objects.Invoice(xsolla_id=666,
                                                  account_id=13,
                                                  purchased_amount=100500,
                                                  is_test=False,
                                                  is_fake=True))

    def test_is_test(self):
        invoice = logic.invoice_from_xsolla_data({'transaction': {'id': 666,
                                                                  'dry_run': 1},
                                                  'user': {'id': 13},
                                                  'purchase': {'virtual_currency': {'quantity': 100500}}})
        self.assertEqual(invoice, objects.Invoice(xsolla_id=666,
                                                  account_id=13,
                                                  purchased_amount=100500,
                                                  is_test=True,
                                                  is_fake=False))
