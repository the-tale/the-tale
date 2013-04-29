# coding: utf-8

from django.db import IntegrityError

from common.utils import testcase

from bank.prototypes import AccountPrototype, InvoicePrototype
from bank.relations import ENTITY_TYPE, CURRENCY_TYPE, INVOICE_STATE


class AccountPrototypeTests(testcase.TestCase):

    def setUp(self):
        super(AccountPrototypeTests, self).setUp()
        self.entity_id = 2
        self.account = AccountPrototype.create(entity_type=ENTITY_TYPE.GAME_ACCOUNT, entity_id=self.entity_id, currency=CURRENCY_TYPE.PREMIUM)


    def test_create(self):
        self.assertEqual(self.account.entity_type, ENTITY_TYPE.GAME_ACCOUNT)
        self.assertEqual(self.account.entity_id, self.entity_id)
        self.assertEqual(self.account.currency, CURRENCY_TYPE.PREMIUM)
        self.assertEqual(self.account.amount, 0)

    def test_duplicate_account(self):
        self.assertRaises(IntegrityError, AccountPrototype.create, entity_type=ENTITY_TYPE.GAME_ACCOUNT, entity_id=self.entity_id, currency=CURRENCY_TYPE.PREMIUM)

    def test_account_with_different_currency(self):
        AccountPrototype.create(entity_type=ENTITY_TYPE.GAME_ACCOUNT, entity_id=self.entity_id, currency=CURRENCY_TYPE.NORMAL)
        self.assertEqual(AccountPrototype._model_class.objects.filter(entity_id=self.entity_id).count(), 2)

    def test_account_with_different_entity_type(self):
        AccountPrototype.create(entity_type=ENTITY_TYPE.GAME_LOGIC, entity_id=self.entity_id, currency=CURRENCY_TYPE.PREMIUM)
        self.assertEqual(AccountPrototype._model_class.objects.filter(entity_id=self.entity_id).count(), 2)

    def test_amount_real_account(self):
        self.account.amount += 100
        self.account.amount -= 10
        self.assertEqual(self.account.amount, 90)

    def test_amount__infinit_account(self):
        self.assertTrue(ENTITY_TYPE.GAME_LOGIC.is_infinite)
        account = AccountPrototype.create(entity_type=ENTITY_TYPE.GAME_LOGIC, entity_id=self.entity_id, currency=CURRENCY_TYPE.PREMIUM)
        old_amount = account.amount

        account.amount += 100
        account.amount -= 10

        self.assertEqual(account.amount, old_amount)

    def test_get_for_or_create__create(self):
        AccountPrototype.get_for_or_create(entity_type=ENTITY_TYPE.GAME_LOGIC, entity_id=self.entity_id, currency=CURRENCY_TYPE.PREMIUM)
        self.assertEqual(AccountPrototype._model_class.objects.filter(entity_id=self.entity_id).count(), 2)

    def test_get_for_or_create__get(self):
        AccountPrototype.get_for_or_create(entity_type=ENTITY_TYPE.GAME_ACCOUNT, entity_id=self.entity_id, currency=CURRENCY_TYPE.PREMIUM)
        self.assertEqual(AccountPrototype._model_class.objects.filter(entity_id=self.entity_id).count(), 1)

    def test_has_money__test_amount_less_then_zero(self):
        self.assertTrue(self.account.has_money(-9999999999999999999))

    def _create_incoming_invoice(self, amount, state=INVOICE_STATE.FROZEN):
        invoice = InvoicePrototype.create(recipient_type=self.account.entity_type,
                                          recipient_id=self.account.entity_id,
                                          sender_type=ENTITY_TYPE.GAME_LOGIC,
                                          sender_id=0,
                                          currency=CURRENCY_TYPE.PREMIUM,
                                          amount=amount)
        invoice.state = state
        invoice.save()

    def _create_outcoming_invoice(self, amount, state=INVOICE_STATE.FROZEN):
        invoice = InvoicePrototype.create(sender_type=self.account.entity_type,
                                          sender_id=self.account.entity_id,
                                          recipient_type=ENTITY_TYPE.GAME_LOGIC,
                                          recipient_id=0,
                                          currency=CURRENCY_TYPE.PREMIUM,
                                          amount=amount)
        invoice.state = state
        invoice.save()


    def test_has_money__incoming_money_freezed(self):
        self.account.amount = 50

        self._create_incoming_invoice(amount=100)

        self._create_incoming_invoice(amount=-1000, state=INVOICE_STATE.CONFIRMED)
        self._create_incoming_invoice(amount=-1000, state=INVOICE_STATE.REQUESTED)

        self.assertTrue(self.account.has_money(50))
        self.assertTrue(self.account.has_money(100))
        self.assertTrue(self.account.has_money(150))
        self.assertFalse(self.account.has_money(151))

        self._create_incoming_invoice(amount=-60)

        self.assertTrue(self.account.has_money(50))
        self.assertTrue(self.account.has_money(90))
        self.assertFalse(self.account.has_money(91))

    def test_has_money__outcoming_money_freezed(self):
        self.account.amount = 50

        self._create_outcoming_invoice(amount=100)

        self._create_incoming_invoice(amount=-1000, state=INVOICE_STATE.CONFIRMED)
        self._create_incoming_invoice(amount=-1000, state=INVOICE_STATE.REQUESTED)

        self.assertFalse(self.account.has_money(0))
        self.assertFalse(self.account.has_money(1))

        self._create_outcoming_invoice(amount=-60)

        self.assertTrue(self.account.has_money(0))
        self.assertTrue(self.account.has_money(10))
        self.assertFalse(self.account.has_money(11))

    def test_has_money__all_money_freezed(self):
        self.account.amount = 10000
        self._create_incoming_invoice(amount=1)
        self._create_incoming_invoice(amount=-10)
        self._create_outcoming_invoice(amount=100)
        self._create_outcoming_invoice(amount=-1000)

        self.assertTrue(self.account.has_money(10000+1-10-100+1000))
        self.assertFalse(self.account.has_money(10000+1-10-100+1000 + 1))


# class InvoicePrototypeTests(testcase.TestCase):

#     def setUp(self):
#         super(InvoicePrototypeTests, self).setUp()
#         self.recipient_id = 3
#         self.sender_id = 8
#         self.amount = 317
#         self.invoice = InvoicePrototype.create(recipient_type=ENTITY_TYPE,
#                                                recipient_id=self.recipient_id,
#                                                sender_type=ENTITY_2_TYPE,
#                                                sender_id=self.sender_id,
#                                                currency=CURRENCY,
#                                                amount=self.amount)


#     def test_create(self):
#         self.assertEqual(self.invoice.recipient_type, ENTITY_TYPE)
#         self.assertEqual(self.invoice.recipient_id, self.recipient_id)
#         self.assertEqual(self.invoice.sender_type, ENTITY_2_TYPE)
#         self.assertEqual(self.invoice.sender_id, self.sender_id)
#         self.assertEqual(self.invoice.amount, self.amount)
#         self.assertTrue(self.invoice.state._is_REQUESTED)

#     def test_freeze(self):
#         self.assertEqual(AccountPrototype._model_class.objects.all().count(), 0)
#         self.invoice.freeze()
#         self.assertEqual(AccountPrototype._model_class.objects.all().count(), 1)

#         account = AccountPrototype(model=AccountPrototype._model_class.objects.all()[0])
#         self.assertEqual(account.amount, 0)
#         self.assertEqual(account.entity_type, ENTITY_TYPE)
#         self.assertEqual(account.entity_id, self.recipient_id)

#     def test_freeze__for_infinite_recipient(self):
#         pass

#     def test_freeze__for_infinite_sender(self):
#         pass

#     def test_freeze__for_infinite_both(self):
#         pass

#     def test_freeze__reject(self):
#         pass

#     def test_freeze__reject_for_infinite_recipient(self):
#         pass

#     def test_freeze__reject_for_infinite_sender(self):
#         pass

#     def test_freeze__reject_for_both(self):
#         pass

#     def test_reject(self):
#         pass

#     def test_reject__not_reqested_state(self):
#         pass

#     def test_confirm(self):
#         pass

#     def test_confirm__not_frozen_state(self):
#         pass

#     def test_cancel(self):
#         pass

#     def test_cancel__not_in_frozen_state(self):
#         pass

#     def test_reset(self):
#         pass

#     def test_reset__not_in_frozen_or_requested_states(self):
#         pass
