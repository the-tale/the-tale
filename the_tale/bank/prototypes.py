# coding: utf-8
import datetime

from django.db import models, IntegrityError, transaction

from the_tale.common.utils.prototypes import BasePrototype
from the_tale.common.utils.logic import get_or_create

from the_tale.bank.models import Invoice, Account
from the_tale.bank.relations import INVOICE_STATE, ENTITY_TYPE, CURRENCY_TYPE
from the_tale.bank.exceptions import BankError
from the_tale.bank.conf import bank_settings


class FakeAccountPrototype(object):

    is_fake = True

    def __init__(self, amount=0, entity_type=ENTITY_TYPE.GAME_ACCOUNT, currency=CURRENCY_TYPE.PREMIUM, entity_id=0):
        self.amount = amount
        self.entity_type = entity_type
        self.currency = currency
        self.entity_id = entity_id

    def get_history_list(self):
        return []


class AccountPrototype(BasePrototype):
    _model_class = Account
    _readonly = ('id', 'entity_type', 'entity_id', 'currency')
    _bidirectional = ()
    _get_by = ('id', )

    is_fake = False

    def get_amount(self):
        if self.entity_type.is_infinite:
            return bank_settings.INFINIT_MONEY_AMOUNT
        return self._model.amount
    def set_amount(self, value):
        if self.entity_type.is_infinite:
            return
        self._model.amount = value
    amount = property(get_amount, set_amount)

    @classmethod
    def get_for(cls, entity_type, entity_id, currency, null_object=False):
        try:
            return cls(model=cls._model_class.objects.get(entity_type=entity_type, entity_id=entity_id, currency=currency))
        except cls._model_class.DoesNotExist:
            if null_object:
                return FakeAccountPrototype(entity_id=entity_id,
                                            entity_type=entity_type,
                                            currency=currency)
            return None

    @classmethod
    def get_for_or_create(cls, entity_type, entity_id, currency):
        return get_or_create(get_method=cls.get_for,
                             create_method=cls.create,
                             exception=IntegrityError,
                             kwargs={'entity_type': entity_type,
                                     'entity_id': entity_id,
                                     'currency': currency})

    @classmethod
    def create(cls, entity_type, entity_id, currency):
        model = cls._model_class.objects.create(entity_type=entity_type,
                                                entity_id=entity_id,
                                                currency=currency)
        return cls(model=model)

    def has_money(self, test_amount):

        if test_amount < 0:
            return True

        # check only "bad variant (when account only spent money)

        frozen_incoming_query = Invoice.objects.filter(recipient_type=self.entity_type,
                                                       recipient_id=self.entity_id,
                                                       currency=self.currency,
                                                       amount__lt=0,
                                                       state=INVOICE_STATE.FROZEN)
        frozen_incoming = frozen_incoming_query.aggregate(frozen_amount=models.Sum('amount'))['frozen_amount']

        frozen_outcoming_query = Invoice.objects.filter(sender_type=self.entity_type,
                                                        sender_id=self.entity_id,
                                                        currency=self.currency,
                                                        amount__gt=0,
                                                        state=INVOICE_STATE.FROZEN)

        frozen_outcoming = frozen_outcoming_query.aggregate(frozen_amount=models.Sum('amount'))['frozen_amount']

        return self.amount + (frozen_incoming if frozen_incoming else 0) - (frozen_outcoming if frozen_outcoming else 0) >= test_amount

    def get_history_list(self):
        condition = models.Q(recipient_type=self.entity_type, recipient_id=self.entity_id) | models.Q(sender_type=self.entity_type, sender_id=self.entity_id)
        invoice_models = list(InvoicePrototype._model_class.objects.filter(state=INVOICE_STATE.CONFIRMED).filter(condition).order_by('-updated_at'))
        return [InvoicePrototype(model=model) for model in invoice_models]

    @classmethod
    def _money_received(cls, from_type, currency=CURRENCY_TYPE.PREMIUM, accounts_ids=None):
        incoming_query = Invoice.objects.filter(recipient_type=ENTITY_TYPE.GAME_ACCOUNT,
                                                sender_type=from_type,
                                                currency=currency,
                                                state=INVOICE_STATE.CONFIRMED,
                                                amount__gt=0)
        if accounts_ids:
            incoming_query = incoming_query.filter(recipient_id__in=accounts_ids)
        incoming_amount = incoming_query.aggregate(total_amount=models.Sum('amount')).get('total_amount')

        outcoming_query = Invoice.objects.filter(sender_type=ENTITY_TYPE.GAME_ACCOUNT,
                                                 recipient_type=from_type,
                                                 currency=currency,
                                                 state=INVOICE_STATE.CONFIRMED,
                                                 amount__lt=0)
        if accounts_ids:
            outcoming_query = outcoming_query.filter(sender_id__in=accounts_ids)
        outcoming_amount = outcoming_query.aggregate(total_amount=models.Sum('amount')).get('total_amount')

        amount = (incoming_amount if incoming_amount else 0) - (outcoming_amount if outcoming_amount else 0)
        return amount if amount else 0

    @classmethod
    def _money_spent(cls, from_type, currency=CURRENCY_TYPE.PREMIUM):
        incoming_query = Invoice.objects.filter(recipient_type=ENTITY_TYPE.GAME_ACCOUNT,
                                                sender_type=from_type,
                                                currency=currency,
                                                state=INVOICE_STATE.CONFIRMED,
                                                amount__lt=0)
        incoming_amount = incoming_query.aggregate(total_amount=models.Sum('amount')).get('total_amount')

        outcoming_query = Invoice.objects.filter(sender_type=ENTITY_TYPE.GAME_ACCOUNT,
                                                 recipient_type=from_type,
                                                 currency=currency,
                                                 state=INVOICE_STATE.CONFIRMED,
                                                 amount__gt=0)

        outcoming_amount = outcoming_query.aggregate(total_amount=models.Sum('amount')).get('total_amount')

        amount = (incoming_amount if incoming_amount else 0) - (outcoming_amount if outcoming_amount else 0)
        return amount if amount else 0


    def save(self):
        self._model.save()


class InvoicePrototype(BasePrototype):
    _model_class = Invoice
    _readonly = ('id', 'updated_at', 'recipient_id', 'recipient_type', 'sender_id', 'sender_type', 'amount', 'currency', 'description', 'operation_uid')
    _bidirectional = ('state',)
    _get_by = ('id', )

    @classmethod
    def get_unprocessed_invoice(cls):
        try:
            return cls(model=cls._model_class.objects.filter(state__in=(INVOICE_STATE.REQUESTED, INVOICE_STATE.FORCED)).order_by('created_at')[0])
        except IndexError:
            return None

    @classmethod
    def check_frozen_expired_invoices(cls):
        return cls._db_filter(state=INVOICE_STATE.FROZEN, updated_at__lt=datetime.datetime.now()-bank_settings.FROZEN_INVOICE_EXPIRED_TIME).exists()

    @classmethod
    def create(cls, recipient_type, recipient_id, sender_type, sender_id, currency, amount, description, operation_uid, force=False):
        model = cls._model_class.objects.create(recipient_type=recipient_type,
                                                recipient_id=recipient_id,
                                                sender_type=sender_type,
                                                sender_id=sender_id,
                                                currency=currency,
                                                amount=amount,
                                                state=INVOICE_STATE.FORCED if force else INVOICE_STATE.REQUESTED,
                                                description=description,
                                                operation_uid=operation_uid)

        return cls(model=model)

    @transaction.atomic
    def freeze(self):

        if not self.state.is_REQUESTED:
            raise BankError(u'try to freeze not requested invoice "%d"' % self.id)

        recipient = AccountPrototype.get_for_or_create(entity_type=self.recipient_type, entity_id=self.recipient_id, currency=self.currency)

        if not recipient.has_money(-self.amount):
            self.state = INVOICE_STATE.REJECTED
            self.save()
            return

        sender = AccountPrototype.get_for_or_create(entity_type=self.sender_type, entity_id=self.sender_id, currency=self.currency)

        if not sender.has_money(self.amount):
            self.state = INVOICE_STATE.REJECTED
            self.save()
            return

        self.state = INVOICE_STATE.FROZEN
        self.save()

    @transaction.atomic
    def confirm(self):
        if not (self.state.is_FROZEN or self.state.is_FORCED):
            raise BankError(u'try to confirm not frozen or forced invoice "%d"' % self.id)

        recipient = AccountPrototype.get_for_or_create(entity_type=self.recipient_type, entity_id=self.recipient_id, currency=self.currency)
        recipient.amount += self.amount
        recipient.save()

        sender = AccountPrototype.get_for_or_create(entity_type=self.sender_type, entity_id=self.sender_id, currency=self.currency)
        sender.amount -= self.amount
        sender.save()

        self.state = INVOICE_STATE.CONFIRMED
        self.save()

    @transaction.atomic
    def force(self):
        self.confirm()

    def cancel(self):
        if not self.state.is_FROZEN:
            raise BankError(u'try to cancel not frozen invoice "%d"' % self.id)

        self.state = INVOICE_STATE.CANCELED
        self.save()

    @classmethod
    def reset_all(cls):
        cls._model_class.objects.filter(state__in=(INVOICE_STATE.FROZEN, INVOICE_STATE.REQUESTED)).update(state=INVOICE_STATE.RESETED)

    def save(self):
        self._model.save()
