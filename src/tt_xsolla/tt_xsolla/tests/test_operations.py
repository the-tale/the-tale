
import random
import asyncio
import dataclasses

from unittest import mock

from aiohttp import test_utils

from tt_web import postgresql as db

from .. import objects
from .. import operations

from . import helpers


class UpdateLoadAccountInfoTests(helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test_load_no_info(self):
        info = await operations.load_account_info(666)
        self.assertEqual(info, None)

    @test_utils.unittest_run_loop
    async def test_save_new_info_and_load(self):
        new_info = helpers.create_account_info(1)

        await operations.update_account_info(db.sql, new_info)

        loaded_info = await operations.load_account_info(1)

        self.assertEqual(new_info, loaded_info)

        not_existed_info = await operations.load_account_info(2)

        self.assertEqual(not_existed_info, None)

    @test_utils.unittest_run_loop
    async def test_update_info_and_load(self):
        old_info = helpers.create_account_info(1, version=1)
        new_info = helpers.create_account_info(1, version=2)
        other_info = helpers.create_account_info(2)

        await operations.update_account_info(db.sql, old_info)
        await operations.update_account_info(db.sql, other_info)
        await operations.update_account_info(db.sql, new_info)

        loaded_info = await operations.load_account_info(new_info.id)
        self.assertEqual(new_info, loaded_info)

        loaded_info = await operations.load_account_info(other_info.id)
        self.assertEqual(other_info, loaded_info)

        not_existed_info = await operations.load_account_info(3)
        self.assertEqual(not_existed_info, None)


class UpdateLoadTokenTests(helpers.BaseTests):

    async def prepair_data(self):
        account_1_info = helpers.create_account_info(1)
        account_2_info = helpers.create_account_info(2)

        await operations.update_account_info(db.sql, account_1_info)
        await operations.update_account_info(db.sql, account_2_info)

        return account_1_info, account_2_info

    @test_utils.unittest_run_loop
    async def test_load_no_token(self):
        token = await operations.load_token(666)
        self.assertEqual(token, None)

    @test_utils.unittest_run_loop
    async def test_save_new_token_and_load(self):
        account_1_info, account_2_info = await self.prepair_data()

        new_token = helpers.create_token(account_1_info.id)

        await operations.update_token(db.sql, new_token)

        loaded_token = await operations.load_token(new_token.account_id)
        self.assertEqual(new_token, loaded_token)

        not_existed_token = await operations.load_token(account_2_info.id)
        self.assertEqual(not_existed_token, None)

    @test_utils.unittest_run_loop
    async def test_update_token_and_load(self):
        account_1_info, account_2_info = await self.prepair_data()

        old_token = helpers.create_token(account_1_info.id)
        new_token = helpers.create_token(account_1_info.id)
        other_token = helpers.create_token(account_2_info.id)

        await operations.update_token(db.sql, old_token)
        await operations.update_token(db.sql, other_token)
        await operations.update_token(db.sql, new_token)

        loaded_token = await operations.load_token(new_token.account_id)
        self.assertEqual(new_token, loaded_token)

        loaded_token = await operations.load_token(other_token.account_id)
        self.assertEqual(other_token, loaded_token)

        not_existed_token = await operations.load_token(3)
        self.assertEqual(not_existed_token, None)


class SyncTokenWithAccountInfoTests(helpers.BaseTests):

    async def prepair_data(self):
        account_1_info = helpers.create_account_info(1)
        account_2_info = helpers.create_account_info(2)

        old_token = helpers.create_token(account_1_info.id)
        new_token = helpers.create_token(account_1_info.id)

        return account_1_info, account_2_info

    @test_utils.unittest_run_loop
    async def test_sync(self):
        info = helpers.create_account_info(1)
        token = helpers.create_token(info.id)

        await operations.sync_token_with_account_info(token, info)

        loaded_info = await operations.load_account_info(info.id)
        self.assertEqual(info, loaded_info)

        loaded_token = await operations.load_token(token.account_id)
        self.assertEqual(token, loaded_token)

    @test_utils.unittest_run_loop
    async def test_error__no_account(self):
        info = helpers.create_account_info(1)
        token = helpers.create_token(info.id)

        error_methdos = ['tt_xsolla.operations.update_token',
                         'tt_xsolla.operations.update_account_info']

        async def error(*argv, **kwargs):
            raise Exception('error')

        with mock.patch(random.choice(error_methdos), error):
            with self.assertRaises(Exception):
                await operations.sync_token_with_account_info(token, info)

        loaded_info = await operations.load_account_info(info.id)
        self.assertEqual(loaded_info, None)

        loaded_token = await operations.load_token(token.account_id)
        self.assertEqual(loaded_token, None)

    @test_utils.unittest_run_loop
    async def test_error__has_account(self):
        original_info = helpers.create_account_info(1)
        original_token = helpers.create_token(original_info.id)

        await operations.sync_token_with_account_info(original_token, original_info)

        new_info = helpers.create_account_info(original_info.id, version=2)
        new_token = helpers.create_token(new_info.id)

        error_methdos = ['tt_xsolla.operations.update_token',
                         'tt_xsolla.operations.update_account_info']

        async def error(*argv, **kwargs):
            raise Exception('error')

        with mock.patch(random.choice(error_methdos), error):
            with self.assertRaises(Exception):
                await operations.sync_token_with_account_info(new_token, new_info)

        loaded_info = await operations.load_account_info(original_info.id)
        self.assertEqual(loaded_info, original_info)

        loaded_token = await operations.load_token(original_token.account_id)
        self.assertEqual(loaded_token, original_token)


class RegisterLoadInvoiceInfoTests(helpers.BaseTests):

    async def prepair_invoice(self):
        info = helpers.create_account_info(1)
        await operations.update_account_info(db.sql, info)
        invoice = helpers.create_invoice(1, info.id)

        return invoice

    @test_utils.unittest_run_loop
    async def test_new_invoice(self):
        invoice = await self.prepair_invoice()

        invoice_id = await operations.register_invoice(invoice)
        self.assertNotEqual(invoice_id, None)

        stored_invoice = await operations.load_invoice(invoice.xsolla_id)
        self.assertEqual(invoice, stored_invoice)

    @test_utils.unittest_run_loop
    async def test_invoice_exists(self):
        invoice = await self.prepair_invoice()

        invoice_id = await operations.register_invoice(invoice)
        self.assertNotEqual(invoice_id, None)

        for wrong_invoice in (invoice,
                              dataclasses.replace(invoice, account_id=invoice.account_id+1),
                              dataclasses.replace(invoice, purchased_amount=invoice.purchased_amount+1)):
            invoice_id = await operations.register_invoice(wrong_invoice)
            self.assertEqual(invoice_id, None)

        stored_invoice = await operations.load_invoice(invoice.xsolla_id)
        self.assertEqual(invoice, stored_invoice)


class LoadAccountInvoicesTests(helpers.BaseTests):

    async def prepair_invoice(self, account_id, xsolla_id):
        info = helpers.create_account_info(account_id)
        await operations.update_account_info(db.sql, info)
        invoice = helpers.create_invoice(xsolla_id, info.id)
        await operations.register_invoice(invoice)

        return invoice

    @test_utils.unittest_run_loop
    async def test_no_invoices(self):
        invoices = await operations.load_account_invoices(666)
        self.assertEqual(invoices, [])

    @test_utils.unittest_run_loop
    async def test_has_invoices(self):
        invoice_1 = await self.prepair_invoice(account_id=666, xsolla_id=1)
        invoice_2 = await self.prepair_invoice(account_id=777, xsolla_id=2)
        invoice_3 = await self.prepair_invoice(account_id=666, xsolla_id=3)

        invoices = await operations.load_account_invoices(666)
        self.assertCountEqual(invoices, [invoice_1, invoice_3])

        invoices = await operations.load_account_invoices(777)
        self.assertCountEqual(invoices, [invoice_2])


class RegisterLoadCancelationsTests(helpers.BaseTests):

    async def prepair_invoice(self):
        info = helpers.create_account_info(1)
        await operations.update_account_info(db.sql, info)
        invoice = helpers.create_invoice(1, info.id)
        await operations.register_invoice(invoice)

        return invoice

    @test_utils.unittest_run_loop
    async def test_new_cancelation(self):
        invoice = await self.prepair_invoice()

        cancellation = objects.Cancellation(account_id=invoice.account_id,
                                            xsolla_id=invoice.xsolla_id)
        is_registered = await operations.register_cancellation(cancellation)

        self.assertTrue(is_registered)

        stored_cancelation = await operations.load_cancelation(invoice.xsolla_id)
        self.assertEqual(stored_cancelation,
                         objects.Cancellation(account_id=invoice.account_id,
                                              xsolla_id=invoice.xsolla_id))

    @test_utils.unittest_run_loop
    async def test_repeated_cancelation(self):
        invoice = await self.prepair_invoice()

        cancellation = objects.Cancellation(account_id=invoice.account_id,
                                            xsolla_id=invoice.xsolla_id)

        is_registered = await operations.register_cancellation(cancellation)
        self.assertTrue(is_registered)

        is_registered = await operations.register_cancellation(cancellation)
        self.assertFalse(is_registered)

        stored_cancelation = await operations.load_cancelation(invoice.xsolla_id)
        self.assertEqual(stored_cancelation,
                         objects.Cancellation(account_id=invoice.account_id,
                                              xsolla_id=invoice.xsolla_id))


class FindAndLockUnprocessedInvoiceTests(helpers.BaseTests):

    async def prepair_invoice(self, account_id, xsolla_id):
        info = helpers.create_account_info(account_id)
        await operations.update_account_info(db.sql, info)
        invoice = helpers.create_invoice(xsolla_id, info.id)
        await operations.register_invoice(invoice)

        return invoice

    @test_utils.unittest_run_loop
    async def test_no_invoices(self):
        invoice_id, invoice = await operations.find_and_lock_unprocessed_invoice(db.sql)

        self.assertEqual(invoice_id, None)
        self.assertEqual(invoice, None)

    @test_utils.unittest_run_loop
    async def test_single_invoice(self):
        expected_invoice = await self.prepair_invoice(100, 1000)

        invoice_id, invoice = await operations.find_and_lock_unprocessed_invoice(db.sql)

        self.assertNotEqual(invoice_id, None)
        self.assertEqual(invoice, expected_invoice)

    @test_utils.unittest_run_loop
    async def test_multiple_invoices(self):
        expected_invoice_1 = await self.prepair_invoice(100, 1000)
        expected_invoice_2 = await self.prepair_invoice(101, 1001)

        async def test_lock(execute, arguments):
            invoice_id, invoice = await operations.find_and_lock_unprocessed_invoice(execute)
            await asyncio.sleep(0.1)
            return invoice

        invoices = await asyncio.gather(db.transaction(test_lock, {}),
                                        db.transaction(test_lock, {}),
                                        db.transaction(test_lock, {}),
                                        db.transaction(test_lock, {}))

        self.assertCountEqual(invoices, (expected_invoice_1, expected_invoice_2, None, None))

    @test_utils.unittest_run_loop
    async def test_all_invoices_processed(self):
        for i in range(1, 5):
            await self.prepair_invoice(100+i, 1000+i)

        for _ in range(1, 5):
            invoice_id, invoice = await operations.find_and_lock_unprocessed_invoice(db.sql)
            await operations.mark_invoice_processed(db.sql, invoice_id)

        invoice_id, invoice = await operations.find_and_lock_unprocessed_invoice(db.sql)

        self.assertEqual(invoice_id, None)
        self.assertEqual(invoice, None)


class MarkInvoiceAsProcessedTests(helpers.BaseTests):

    async def prepair_invoice(self, account_id, xsolla_id):
        info = helpers.create_account_info(account_id)
        await operations.update_account_info(db.sql, info)
        invoice = helpers.create_invoice(xsolla_id, info.id)

        return await operations.register_invoice(invoice)

    @test_utils.unittest_run_loop
    async def test_mark(self):
        invoice_1_id = await self.prepair_invoice(100, 1000)
        invoice_2_id = await self.prepair_invoice(101, 1001)

        await operations.mark_invoice_processed(db.sql, invoice_1_id)

        results_1 = await db.sql('SELECT * FROM invoices WHERE id=%(id)s',
                                 {'id': invoice_1_id})
        self.assertNotEqual(results_1[0]['processed_at'], None)

        results_2 = await db.sql('SELECT * FROM invoices WHERE id=%(id)s',
                                 {'id': invoice_2_id})
        self.assertEqual(results_2[0]['processed_at'], None)

        await operations.mark_invoice_processed(db.sql, invoice_1_id)

        results_3 = await db.sql('SELECT * FROM invoices WHERE id=%(id)s',
                                 {'id': invoice_1_id})
        self.assertEqual(results_3[0]['processed_at'], results_1[0]['processed_at'])

        await operations.mark_invoice_processed(db.sql, invoice_2_id)

        results_4 = await db.sql('SELECT * FROM invoices WHERE id=%(id)s',
                                 {'id': invoice_2_id})
        self.assertNotEqual(results_4[0]['processed_at'], None)
