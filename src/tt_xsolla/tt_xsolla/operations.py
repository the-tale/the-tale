
from psycopg2.extras import Json as PGJson

from tt_web import postgresql as db

from . import objects
from . import relations


def row_to_account_info(row):
    return objects.AccountInfo(id=row['id'],
                               name=row['data']['name'],
                               email=row['data']['email'],
                               return_url=row['data']['return_url'],
                               state=relations.ACCOUNT_INFO_STATE(row['state']))


def row_to_token(row):
    return objects.Token(value=row['value'],
                         account_id=row['account'],
                         expire_at=row['expire_at'].replace(tzinfo=None))


def row_to_invoice(row):
    return objects.Invoice(xsolla_id=row['xsolla_id'],
                           account_id=row['account'],
                           purchased_amount=row['data']['purchased_amount'],
                           is_test=row['is_test'],
                           is_fake=row['is_fake'])


def row_to_cancelation(row):
    return objects.Cancellation(account_id=row['account'],
                                xsolla_id=row['xsolla_id'])


async def load_account_info(account_id):
    results = await db.sql('SELECT * FROM accounts_infos WHERE id=%(id)s',
                           {'id': account_id})

    if results:
        return row_to_account_info(results[0])

    return None


async def update_account_info(execute, account_info):
    data = {'name': account_info.name,
            'email': account_info.email,
            'return_url': account_info.return_url}

    await execute('''INSERT INTO accounts_infos (id, state, data, created_at, updated_at)
                     VALUES (%(id)s, %(state)s, %(data)s, NOW(), NOW())
                     ON CONFLICT (id) DO UPDATE SET data=EXCLUDED.data,
                                                    state=EXCLUDED.state,
                                                    updated_at=NOW()''',
                  {'id': account_info.id,
                   'state': account_info.state.value,
                   'data': PGJson(data)})


async def load_token(account_id):
    results = await db.sql('SELECT * FROM tokens WHERE account=%(id)s',
                           {'id': account_id})

    if results:
        return row_to_token(results[0])

    return None


async def update_token(execute, token):
    await execute('''INSERT INTO tokens (account, value, expire_at, created_at, updated_at)
                     VALUES (%(account_id)s, %(value)s, %(expire_at)s, NOW(), NOW())
                     ON CONFLICT (account) DO UPDATE SET value=EXCLUDED.value,
                                                         expire_at=EXCLUDED.expire_at,
                                                         updated_at=NOW()''',
                 {'account_id': token.account_id,
                  'value': token.value,
                  'expire_at': token.expire_at})


async def sync_token_with_account_info(token, account_info):
    return await db.transaction(_sync_token_with_account_info, {'account_info': account_info,
                                                                'token': token})


async def _sync_token_with_account_info(execute, arguments):
    account_info = arguments['account_info']
    token = arguments['token']

    await update_token(execute, token)

    await update_account_info(execute, account_info)


async def load_invoice(xsolla_id):
    results = await db.sql('SELECT * FROM invoices where xsolla_id=%(xsolla_id)s', {'xsolla_id': xsolla_id})

    if not results:
        return None

    return row_to_invoice(results[0])


async def register_invoice(invoice):

    data = {'purchased_amount': invoice.purchased_amount}

    results = await db.sql('''INSERT INTO invoices (xsolla_id, account, data, is_test, is_fake, created_at, updated_at, processed_at)
                              VALUES (%(xsolla_id)s, %(account_id)s, %(data)s, %(is_test)s, %(is_fake)s, NOW(), NOW(), NULL)
                              ON CONFLICT (xsolla_id) DO NOTHING
                              RETURNING id''',
                           {'xsolla_id': invoice.xsolla_id,
                            'account_id': invoice.account_id,
                            'is_test': invoice.is_test,
                            'is_fake': invoice.is_fake,
                            'data': PGJson(data)})

    if not results:
        return None

    return results[0]['id']


async def load_account_invoices(account_id):
    results = await db.sql('SELECT * FROM invoices where account=%(account_id)s', {'account_id': account_id})
    return [row_to_invoice(row) for row in results]


async def load_cancelation(xsolla_id):
    results = await db.sql('SELECT * FROM cancellations where xsolla_id=%(xsolla_id)s',
                           {'xsolla_id': xsolla_id})

    if not results:
        return None

    return row_to_cancelation(results[0])


async def register_cancellation(cancellation):
    data = {}

    results = await db.sql('''INSERT INTO cancellations (account, xsolla_id, data, created_at, updated_at, processed_at)
                              VALUES (%(account_id)s, %(xsolla_id)s, %(data)s, NOW(), NOW(), NULL)
                              ON CONFLICT (xsolla_id) DO NOTHING
                              RETURNING id''',
                           {'xsolla_id': cancellation.xsolla_id,
                            'account_id': cancellation.account_id,
                            'data': PGJson(data)})

    return bool(results)


async def load_account_cancelations(account_id):
    results = await db.sql('SELECT * FROM cancellations WHERE account=%(account_id)s', {'account_id': account_id})
    return [row_to_cancelation(row) for row in results]


async def find_and_lock_unprocessed_invoice(execute):
    results = await execute('SELECT * FROM invoices WHERE processed_at IS NULL LIMIT 1 FOR UPDATE SKIP LOCKED')

    if not results:
        return None, None

    return results[0]['id'], row_to_invoice(results[0])


async def mark_invoice_processed(execute, invoice_id):
    await execute('UPDATE invoices SET updated_at=NOW(), processed_at=NOW() WHERE id=%(invoice_id)s AND processed_at IS NULL',
                  {'invoice_id': invoice_id})


async def clean_database():
    await db.sql('TRUNCATE tokens, accounts_infos, invoices, cancellations')
