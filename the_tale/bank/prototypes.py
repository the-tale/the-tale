# coding: utf-8

from django.db import models

from dext.utils.decorators import nested_commit_on_success

from common.utils.prototypes import BasePrototype

from bank.models import Invoice, Account
from bank.relations import INVOICE_STATE, ENTITY_TYPE, CURRENCY_TYPE
from bank.exceptions import BankError
from bank.conf import bank_settings


class FakeAccountPrototype(object):

    def __init__(self, amount=0, entity_type=ENTITY_TYPE.GAME_ACCOUNT, currency=CURRENCY_TYPE.PREMIUM, entity_id=0):
        self.amount = amount
        self.entity_type = entity_type
        self.currency = currency
        self.entity_id = entity_id

    def get_history_list(self):
        return []


class AccountPrototype(BasePrototype):
    _model_class = Account
    _readonly = ('entity_type', 'entity_id', 'currency')
    _bidirectional = ()
    _get_by = ('id', )

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
        account = cls.get_for(entity_type, entity_id, currency)

        if account is not None:
            return account

        return cls.create(entity_type, entity_id, currency)

    @classmethod
    def create(cls, entity_type, entity_id, currency):
        model = cls._model_class.objects.create(entity_type=entity_type,
                                                entity_id=entity_id,
                                                currency=currency)
        return cls(model=model)

    def has_money(self, test_amount):

        if test_amount < 0:
            return True

        frozen_incoming_query = Invoice.objects.filter(recipient_type=self.entity_type,
                                                       recipient_id=self.entity_id,
                                                       currency=self.currency,
                                                       state=INVOICE_STATE.FROZEN)
        frozen_incoming = frozen_incoming_query.aggregate(frozen_amount=models.Sum('amount'))['frozen_amount']

        frozen_outcoming_query = Invoice.objects.filter(sender_type=self.entity_type,
                                                        sender_id=self.entity_id,
                                                        currency=self.currency,
                                                        state=INVOICE_STATE.FROZEN)

        frozen_outcoming = frozen_outcoming_query.aggregate(frozen_amount=models.Sum('amount'))['frozen_amount']

        return self.amount + (frozen_incoming if frozen_incoming else 0) - (frozen_outcoming if frozen_outcoming else 0) >= test_amount

    def get_history_list(self):
        condition = models.Q(recipient_type=self.entity_type, recipient_id=self.entity_id) | models.Q(sender_type=self.entity_type, sender_id=self.entity_id)
        invoice_models = list(InvoicePrototype._model_class.objects.filter(state=INVOICE_STATE.CONFIRMED).filter(condition).order_by('-updated_at'))
        return [InvoicePrototype(model=model) for model in invoice_models]

    def save(self):
        self._model.save()


class InvoicePrototype(BasePrototype):
    _model_class = Invoice
    _readonly = ('id', 'updated_at', 'recipient_id', 'recipient_type', 'sender_id', 'sender_type', 'amount', 'currency', 'description')
    _bidirectional = ('state',)
    _get_by = ('id', )

    @classmethod
    def get_unprocessed_invoice(cls):
        try:
            return cls(model=cls._model_class.objects.filter(state=INVOICE_STATE.REQUESTED).order_by('created_at')[0])
        except IndexError:
            return None

    @classmethod
    def create(cls, recipient_type, recipient_id, sender_type, sender_id, currency, amount, description):
        model = cls._model_class.objects.create(recipient_type=recipient_type,
                                                recipient_id=recipient_id,
                                                sender_type=sender_type,
                                                sender_id=sender_id,
                                                currency=currency,
                                                amount=amount,
                                                state=INVOICE_STATE.REQUESTED,
                                                description=description)

        return cls(model=model)

    @nested_commit_on_success
    def freeze(self):

        if not self.state._is_REQUESTED:
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

    @nested_commit_on_success
    def confirm(self):
        if not self.state._is_FROZEN:
            raise BankError(u'try to confirm not frozen invoice "%d"' % self.id)

        recipient = AccountPrototype.get_for(entity_type=self.recipient_type, entity_id=self.recipient_id, currency=self.currency)
        recipient.amount += self.amount
        recipient.save()

        sender = AccountPrototype.get_for(entity_type=self.sender_type, entity_id=self.sender_id, currency=self.currency)
        sender.amount -= self.amount
        sender.save()

        self.state = INVOICE_STATE.CONFIRMED
        self.save()

    def cancel(self):
        if not self.state._is_FROZEN:
            raise BankError(u'try to cancel not frozen invoice "%d"' % self.id)

        self.state = INVOICE_STATE.CANCELED
        self.save()

    @classmethod
    def reset_all(self):
        self._model_class.objects.filter(state__in=(INVOICE_STATE.FROZEN, INVOICE_STATE.REQUESTED)).update(state=INVOICE_STATE.RESETED)

    def save(self):
        self._model.save()
