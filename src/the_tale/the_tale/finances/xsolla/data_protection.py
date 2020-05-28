
import smart_imports

smart_imports.all()


def collect_data(account_id):
    data = []

    for invoice in models.Invoice.objects.filter(bank_id=account_id):
        data.append(('xsolla_invoice', {'created_at': invoice.created_at,
                                        'updated_at': invoice.updated_at,
                                        'state': invoice.state,
                                        'xsolla': {'id': invoice.xsolla_id,
                                                   'v1': invoice.xsolla_v1,
                                                   'v2': invoice.xsolla_v2,
                                                   'v3': invoice.xsolla_v3},
                                        'comment': invoice.comment,
                                        'pay_result': invoice.pay_result,
                                        'date': invoice.date}))

    return data


def remove_data(account_id, v1_filler=None):
    # мы не удаляем идентификаторы платежей в XSolla, так как эта наша информация
    # пользователь может обратиться в XSolla, чтобы они удалили информацию о нём
    #
    # мы удаляем параметры запроса (v1, v2, v3), так как в них содержится личная информация игрока (email)

    if v1_filler is None:
        v1_filler = f'removed-{uuid.uuid4().hex}'

    models.Invoice.objects.filter(bank_id=account_id).update(xsolla_v1=v1_filler,
                                                             xsolla_v2=None,
                                                             xsolla_v3=None,
                                                             comment='')
