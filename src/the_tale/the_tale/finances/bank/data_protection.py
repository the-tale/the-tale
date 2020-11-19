
import smart_imports

smart_imports.all()


def collect_data(account_id):
    data = []

    account = accounts_prototypes.AccountPrototype.get_by_id(account_id)
    bank_account = account.bank_account

    condition = django_models.Q(recipient_type=bank_account.entity_type,
                                recipient_id=bank_account.entity_id) | django_models.Q(sender_type=bank_account.entity_type,
                                                                                       sender_id=bank_account.entity_id)

    invoices = [prototypes.InvoicePrototype(model=model) for model in models.Invoice.objects.filter(condition)]

    for invoice in invoices:
        invoice_data = {'updated_at': invoice.updated_at,
                        'created_at': invoice._model.created_at,
                        'recipient_id': invoice.recipient_id,
                        'recipient_type': invoice.recipient_type,
                        'sender_id': invoice.sender_id,
                        'sender_type': invoice.sender_type,
                        'amount': invoice.amount,
                        'currency': invoice.currency,
                        'state': invoice.state,
                        'description_for_recipient': invoice.description_for_recipient,
                        'description_for_sender': invoice.description_for_sender}

        # адресатов/получателей отображаем только если это прямой перевод
        # в остальных случаях эта информация либо очевидна (покупка печенек), либо нарушает конфиденциальность других игроков (рынок)
        if invoice.operation_uid != 'transfer-money-between-accounts-transfer':
            del invoice_data['recipient_id']
            del invoice_data['sender_id']

        data.append(('game_invoice', invoice_data))

    return data


def remove_data(account_id):
    # Ничего не удаляем, так как:
    # - эта информация критична для функционирования игры
    # - не предоставляет достаточно данных для определения человека
    # Данные об игроках в платёжных аггрегаторах удаляются в логике работы с платёжными аггрегаторам
    pass
