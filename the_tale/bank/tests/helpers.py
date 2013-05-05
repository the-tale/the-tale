# coding: utf-8

from bank.prototypes import InvoicePrototype, AccountPrototype
from bank.relations import ENTITY_TYPE, CURRENCY_TYPE, INVOICE_STATE


class BankTestsMixin(object):

    def create_bank_account(self, entity_id):
        return AccountPrototype.create(entity_type=ENTITY_TYPE.GAME_ACCOUNT, entity_id=entity_id, currency=CURRENCY_TYPE.PREMIUM)

    def create_invoice(self,
                       recipient_type=ENTITY_TYPE.GAME_ACCOUNT,
                       recipient_id=3,
                       sender_type=ENTITY_TYPE.GAME_LOGIC,
                       sender_id=8,
                       currency=CURRENCY_TYPE.PREMIUM,
                       amount=317,
                       state=None,
                       description='invoice-description'):
        invoice = InvoicePrototype.create(recipient_type=recipient_type,
                                          recipient_id=recipient_id,
                                          sender_type=sender_type,
                                          sender_id=sender_id,
                                          currency=currency,
                                          amount=amount,
                                          description=description)
        if state is not None:
            invoice.state = state
            invoice.save()

        return invoice

    def create_entity_history(self, entity_id):

        for state in INVOICE_STATE._records:
            new_invoices = [
                self.create_invoice(recipient_id=entity_id, description='first-invoice-description-%s' % state, state=state),
                self.create_invoice(recipient_id=entity_id, description='second-invoice-description-%s' % state, state=state),
                self.create_invoice(recipient_id=entity_id + 1, description='third-invoice-description-%s % state', state=state),

                self.create_invoice(sender_id=entity_id, sender_type=ENTITY_TYPE.GAME_ACCOUNT, description='fourth-invoice-description-%s' % state, state=state),
                self.create_invoice(sender_id=entity_id, sender_type=ENTITY_TYPE.GAME_ACCOUNT, description='fifth-invoice-description-%s' % state, state=state),
                self.create_invoice(sender_id=entity_id + 1, sender_type=ENTITY_TYPE.GAME_ACCOUNT, description='sixth-invoice-description-%s' % state, state=state),

                self.create_invoice(sender_id=entity_id, sender_type=ENTITY_TYPE.GAME_LOGIC, description='seventh-invoice-description-%s' % state, state=state),
                self.create_invoice(sender_id=entity_id, sender_type=ENTITY_TYPE.GAME_LOGIC, description='eighth-invoice-description-%s' % state, state=state),
                self.create_invoice(sender_id=entity_id + 1, sender_type=ENTITY_TYPE.GAME_LOGIC, description='ninth-invoice-description-%s' % state, state=state) ]

            if state._is_CONFIRMED:
                invoices = new_invoices

        return [invoices[4],
                invoices[3],
                invoices[1],
                invoices[0]]
