# coding: utf-8

from django.core.management.base import BaseCommand
from django.db import models

from the_tale.accounts.prototypes import AccountPrototype

from the_tale.bank.prototypes import InvoicePrototype
from the_tale.bank.relations import INVOICE_STATE, ENTITY_TYPE, CURRENCY_TYPE


class Command(BaseCommand):

    help = 'Show actions statistics'

    def handle(self, *args, **options):

        actions = set(AccountPrototype._db_exclude(action_id=None).values_list('action_id', flat=True).order_by('action_id').distinct())

        for action_id in actions:
            print
            print '----%s----' % action_id
            registered_ids = set(AccountPrototype._db_filter(action_id=action_id, is_fast=False).values_list('id', flat=True))

            print 'registrations: %d' % len(registered_ids)

            payers_ids = set(InvoicePrototype._db_filter(models.Q(state=INVOICE_STATE.CONFIRMED)|models.Q(state=INVOICE_STATE.FORCED),
                                                        sender_type=ENTITY_TYPE.XSOLLA,
                                                        currency=CURRENCY_TYPE.PREMIUM).values_list('recipient_id', flat=True))

            payers_ids &= registered_ids

            print 'payers: %d' % len(payers_ids)

            amounts = InvoicePrototype._db_filter(models.Q(state=INVOICE_STATE.CONFIRMED)|models.Q(state=INVOICE_STATE.FORCED),
                                                  sender_type=ENTITY_TYPE.XSOLLA,
                                                  recipient_id__in=payers_ids,
                                                  currency=CURRENCY_TYPE.PREMIUM).values_list('amount', flat=True)

            amount = sum(amounts)

            print 'total gold: %d' % amount

            if registered_ids:
                print 'per account: %.2f' % (float(amount) / len(registered_ids))

            if payers_ids:
                print 'per payer: %.2f' % (float(amount) / len(payers_ids))
