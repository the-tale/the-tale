
import smart_imports

smart_imports.all()


class BankTestsMixin:

    def create_bank_account(self, entity_id, amount=0):
        account = prototypes.AccountPrototype.create(entity_type=relations.ENTITY_TYPE.GAME_ACCOUNT, entity_id=entity_id, currency=relations.CURRENCY_TYPE.PREMIUM)

        account.amount = amount
        account.save()

        return account

    def create_invoice(self,
                       recipient_type=relations.ENTITY_TYPE.GAME_ACCOUNT,
                       recipient_id=3,
                       sender_type=relations.ENTITY_TYPE.GAME_LOGIC,
                       sender_id=8,
                       currency=relations.CURRENCY_TYPE.PREMIUM,
                       amount=317,
                       state=None,
                       description_for_sender='invoice-description-for-sender',
                       description_for_recipient='invoice-description-for-recipient',
                       operation_uid='test-uid',
                       force=False):
        invoice = prototypes.InvoicePrototype.create(recipient_type=recipient_type,
                                                     recipient_id=recipient_id,
                                                     sender_type=sender_type,
                                                     sender_id=sender_id,
                                                     currency=currency,
                                                     amount=amount,
                                                     description_for_sender=description_for_sender,
                                                     description_for_recipient=description_for_recipient,
                                                     operation_uid=operation_uid,
                                                     force=force)
        if state is not None:
            invoice.state = state
            invoice.save()

        return invoice

    def create_entity_history(self, entity_id):

        for state in relations.INVOICE_STATE.records:
            new_invoices = [
                self.create_invoice(recipient_id=entity_id,
                                    description_for_sender='first-invoice-description-for-sender-%s' % state,
                                    description_for_recipient='first-invoice-description-for-recipient-%s' % state,
                                    state=state),
                self.create_invoice(recipient_id=entity_id,
                                    description_for_sender='second-invoice-description-for-sender-%s' % state,
                                    description_for_recipient='second-invoice-description-for-recipient-%s' % state,
                                    state=state),
                self.create_invoice(recipient_id=entity_id + 1,
                                    description_for_sender='third-invoice-description-for-sender-%s % state',
                                    description_for_recipient='third-invoice-description-for-recipient-%s % state',
                                    state=state),

                self.create_invoice(sender_id=entity_id,
                                    sender_type=relations.ENTITY_TYPE.GAME_ACCOUNT,
                                    description_for_sender='fourth-invoice-description-for-sender-%s' % state,
                                    description_for_recipient='fourth-invoice-description-for-recipient-%s' % state,
                                    state=state),
                self.create_invoice(sender_id=entity_id,
                                    sender_type=relations.ENTITY_TYPE.GAME_ACCOUNT,
                                    description_for_sender='fifth-invoice-description-for-sender-%s' % state,
                                    description_for_recipient='fifth-invoice-description-for-recipient-%s' % state,
                                    state=state),
                self.create_invoice(sender_id=entity_id + 1,
                                    sender_type=relations.ENTITY_TYPE.GAME_ACCOUNT,
                                    description_for_sender='sixth-invoice-description-for-sender-%s' % state,
                                    description_for_recipient='sixth-invoice-description-for-recipient-%s' % state,
                                    state=state),

                self.create_invoice(sender_id=entity_id,
                                    sender_type=relations.ENTITY_TYPE.GAME_LOGIC,
                                    description_for_sender='seventh-invoice-description-for-sender-%s' % state,
                                    description_for_recipient='seventh-invoice-description-for-recipient-%s' % state,
                                    state=state),
                self.create_invoice(sender_id=entity_id,
                                    sender_type=relations.ENTITY_TYPE.GAME_LOGIC,
                                    description_for_sender='eighth-invoice-description-for-sender-%s' % state,
                                    description_for_recipient='eighth-invoice-description-for-recipient-%s' % state,
                                    state=state),
                self.create_invoice(sender_id=entity_id + 1,
                                    sender_type=relations.ENTITY_TYPE.GAME_LOGIC,
                                    description_for_sender='ninth-invoice-description-for-sender-%s' % state,
                                    description_for_recipient='ninth-invoice-description-for-recipient-%s' % state,
                                    state=state)]

            if state.is_CONFIRMED:
                invoices = new_invoices

        return [invoices[4],
                invoices[3],
                invoices[1],
                invoices[0]]
