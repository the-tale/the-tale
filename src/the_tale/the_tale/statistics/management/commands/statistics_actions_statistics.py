
import smart_imports

smart_imports.all()


class Command(utilities_base.Command):

    help = 'Show actions statistics'

    LOCKS = ['portal_commands']

    def _handle(self, *args, **options):

        actions = set(accounts_prototypes.AccountPrototype._db_exclude(action_id=None).values_list('action_id', flat=True).order_by('action_id').distinct())

        for action_id in actions:
            self.logger.info('')
            self.logger.info('----%s----' % action_id)
            registered_ids = set(accounts_prototypes.AccountPrototype._db_filter(action_id=action_id, is_fast=False).values_list('id', flat=True))

            self.logger.info('registrations: %d' % len(registered_ids))

            payers_ids = set(bank_prototypes.InvoicePrototype._db_filter(django_models.Q(state=bank_relations.INVOICE_STATE.CONFIRMED) | django_models.Q(state=bank_relations.INVOICE_STATE.FORCED),
                                                                         sender_type=bank_relations.ENTITY_TYPE.XSOLLA,
                                                                         currency=bank_relations.CURRENCY_TYPE.PREMIUM).values_list('recipient_id', flat=True))

            payers_ids &= registered_ids

            self.logger.info('payers: %d' % len(payers_ids))

            amounts = bank_prototypes.InvoicePrototype._db_filter(django_models.Q(state=bank_relations.INVOICE_STATE.CONFIRMED) | django_models.Q(state=bank_relations.INVOICE_STATE.FORCED),
                                                                  sender_type=bank_relations.ENTITY_TYPE.XSOLLA,
                                                                  recipient_id__in=payers_ids,
                                                                  currency=bank_relations.CURRENCY_TYPE.PREMIUM).values_list('amount', flat=True)

            amount = sum(amounts)

            self.logger.info('total gold: %d' % amount)

            if registered_ids:
                self.logger.info('per account: %.2f' % (float(amount) / len(registered_ids)))

            if payers_ids:
                self.logger.info('per payer: %.2f' % (float(amount) / len(payers_ids)))
