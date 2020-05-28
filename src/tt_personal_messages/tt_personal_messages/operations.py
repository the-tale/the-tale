
import asyncio
import itertools

from tt_web import postgresql as db

from . import objects
from . import relations


def message_from_row(row):
    return objects.Message(id=row['id'],
                           sender=row['sender'],
                           recipients=row['recipients'],
                           body=row['body'],
                           created_at=row['created_at'],
                           visible=row['visible'])


async def new_messages_number(account_id):
    result = await db.sql('SELECT new_messages_number FROM accounts WHERE id=%(id)s', {'id': account_id})
    return result[0]['new_messages_number'] if result else 0


async def read_messages(account_id):
    await db.sql('UPDATE accounts SET new_messages_number=0 WHERE id=%(id)s', {'id': account_id})


async def create_message(sender_id, recipients_ids, body):
    result = await db.sql('''INSERT INTO messages (sender, recipients, body, created_at, updated_at)
                             VALUES (%(sender)s, %(recipients)s, %(body)s, NOW(), NOW())
                             RETURNING id''',
                          {'sender': sender_id,
                           'recipients': recipients_ids,
                           'body': body})

    return result[0]['id']


async def create_visibility(account_id, message_id):
    await db.sql('''INSERT INTO visibilities (account, message, visible, created_at, updated_at)
                    VALUES (%(account)s, %(message)s, TRUE, NOW(), NOW())''',
                 {'account': account_id, 'message': message_id})


async def add_to_conversation(account_id, partner_id, message_id):
    account_1_id, account_2_id = min(account_id, partner_id), max(account_id, partner_id)

    await db.sql('''INSERT INTO conversations (account_1, account_2, message, created_at, updated_at)
                    VALUES (%(account_1_id)s, %(account_2_id)s, %(message)s, NOW(), NOW())''',
                 {'account_1_id': account_1_id, 'account_2_id': account_2_id, 'message': message_id})


async def get_contacts(account_id):
    result = await db.sql('SELECT account_1, account_2 FROM conversations WHERE %(id)s IN (account_1, account_2) GROUP BY account_1, account_2', {'id': account_id})

    contacts = {row['account_1'] for row in result}
    contacts.update(row['account_2'] for row in result)

    if contacts:
        contacts.remove(account_id)

    return contacts


async def increment_new_messages(account_id):
    try:
        await db.sql('''INSERT INTO accounts (id, new_messages_number, created_at, updated_at)
                        VALUES (%(account_id)s, 1, NOW(), NOW())
                        ON CONFLICT (id) DO UPDATE SET new_messages_number=accounts.new_messages_number + 1''',
                     {'account_id': account_id})
    except Exception as e:
        print(e)


async def send_message(sender_id, recipients_ids, body):
    recipients_ids = list(set(recipients_ids))

    if sender_id in recipients_ids:
        recipients_ids.remove(sender_id)

    if not recipients_ids:
        return None

    message_id = await create_message(sender_id, recipients_ids, body)

    tasks = [create_visibility(sender_id, message_id=message_id)]

    for recipient_id in recipients_ids:
        tasks.extend((create_visibility(recipient_id, message_id=message_id),
                      add_to_conversation(sender_id, recipient_id, message_id=message_id),
                      increment_new_messages(recipient_id)))

    await asyncio.wait(tasks)

    return message_id


async def hide_message(account_id, message_id):
    await db.sql('UPDATE visibilities SET visible=FALSE WHERE account=%(account_id)s and message=%(message_id)s',
                 {'account_id': account_id, 'message_id': message_id})


async def hide_all_messages(account_id):
    await db.sql('UPDATE visibilities SET visible=FALSE WHERE account=%(account_id)s',
                 {'account_id': account_id})


async def hide_conversation(account_id, partner_id):
    account_1_id, account_2_id = min(account_id, partner_id), max(account_id, partner_id)

    await db.sql('''UPDATE visibilities as v
                    SET visible=FALSE
                    FROM conversations as c
                    WHERE v.account=%(account_id)s AND
                          v.message=c.message AND
                          c.account_1 = %(account_1_id)s AND
                          c.account_2 = %(account_2_id)s''',
                 {'account_id': account_id,
                  'account_1_id': account_1_id,
                  'account_2_id': account_2_id})


async def old_messages_ids(accounts_ids, barrier):
    result = await db.sql('SELECT id FROM messages WHERE sender = ANY (%(accounts_ids)s) AND created_at<%(barrier)s',
                          {'accounts_ids': accounts_ids, 'barrier': barrier})

    return [row['id'] for row in result]


async def candidates_to_remove_ids():
    result = await db.sql('''SELECT message FROM visibilities
                             GROUP BY message
                             HAVING every(NOT visible)''')

    return [row['message'] for row in result]


async def remove_messages(messages_ids):
    await db.transaction(_remove_messages, {'messages_ids': messages_ids})


async def _remove_messages(execute, arguments):

    messages_ids = arguments['messages_ids']

    await execute('DELETE FROM visibilities WHERE message = ANY (%(messages_ids)s)', {'messages_ids': messages_ids})
    await execute('DELETE FROM conversations WHERE message = ANY (%(messages_ids)s)', {'messages_ids': messages_ids})
    await execute('DELETE FROM messages WHERE id = ANY (%(messages_ids)s)', {'messages_ids': messages_ids})


async def load_messages(account_id, type, text=None, offset=0, limit=None, visibility=True):
    if text is None:
        text_filter = ''
    else:
        text = '%{}%'.format(text)
        text_filter = 'AND m.body ILIKE %(text)s'

    limit_filter = '' if limit is None else 'LIMIT %(limit)s'

    if type.is_SENDER:
        type_filter = 'AND m.sender=%(account_id)s'
    else:
        type_filter = 'AND m.sender<>%(account_id)s'

    if visibility is None:
        visibility_filter = 'TRUE'
    elif visibility:
        visibility_filter = 'v.visible'
    else:
        visibility_filter = '(NOT v.visible)'

    sql_count = f'''SELECT count(*) as total
                    FROM visibilities AS v
                    JOIN messages AS m ON m.id = v.message
                    WHERE v.account=%(account_id)s AND
                          {visibility_filter}
                          {type_filter}
                          {text_filter}'''

    sql = f'''SELECT m.id AS id,
                     m.sender AS sender,
                     m.recipients AS recipients,
                     m.body AS body,
                     m.created_at AS created_at,
                     v.visible as visible
             FROM visibilities AS v
             JOIN messages AS m ON m.id = v.message
             WHERE v.account=%(account_id)s AND
                   {visibility_filter}
                   {type_filter}
                   {text_filter}
             ORDER BY m.created_at DESC
             {limit_filter}
             OFFSET %(offset)s'''

    arguments = {'account_id': account_id,
                 'type': type.value,
                 'offset': offset,
                 'limit': limit,
                 'text': text}

    tasks = [db.sql(sql_count, arguments),
             db.sql(sql, arguments)]

    count_results, messages_result = await asyncio.gather(*tasks)

    return count_results[0]['total'], [message_from_row(row) for row in messages_result]


async def load_message(account_id, message_id, visibility=True):
    if visibility is None:
        visibility_filter = 'TRUE'
    elif visibility:
        visibility_filter = 'v.visible'
    else:
        visibility_filter = '(NOT v.visible)'

    sql = f'''SELECT m.id AS id,
                     m.sender AS sender,
                     m.recipients AS recipients,
                     m.body AS body,
                     m.created_at AS created_at,
                     v.visible as visible
              FROM visibilities AS v
              JOIN messages AS m ON m.id = v.message
              WHERE v.account=%(account_id)s AND
                    {visibility_filter} AND
                    m.id=%(message_id)s'''

    result = await db.sql(sql, {'account_id': account_id, 'message_id': message_id})

    if not result:
        return None

    return message_from_row(result[0])


async def load_conversation(account_id, partner_id, text=None, offset=0, limit=None):

    if text is None:
        text_filter = ''
    else:
        text = '%{}%'.format(text)
        text_filter = 'AND m.body ILIKE %(text)s'

    limit_filter = '' if limit is None else 'LIMIT %(limit)s'

    account_1_id, account_2_id = min(account_id, partner_id), max(account_id, partner_id)

    sql_count = '''SELECT count(*) as total
                   FROM messages AS m
                   JOIN visibilities AS v ON m.id = v.message
                   JOIN conversations AS c ON m.id = c.message
                   WHERE v.visible AND
                         v.account=%(account_id)s AND
                         c.account_1=%(account_1_id)s AND
                         c.account_2=%(account_2_id)s
                         {text_filter}'''.format(text_filter=text_filter)

    sql = '''SELECT m.id AS id,
                    m.sender AS sender,
                    m.recipients AS recipients,
                    m.body AS body,
                    m.created_at AS created_at,
                    v.visible as visible
             FROM messages AS m
             JOIN visibilities AS v ON m.id = v.message
             JOIN conversations AS c ON m.id = c.message
             WHERE v.visible AND
                   v.account=%(account_id)s AND
                   c.account_1=%(account_1_id)s AND
                   c.account_2=%(account_2_id)s
                   {text_filter}
             ORDER BY m.created_at DESC
             {limit_filter}
             OFFSET %(offset)s'''.format(text_filter=text_filter,
                                         limit_filter=limit_filter)

    arguments = {'account_1_id': account_1_id,
                 'account_2_id': account_2_id,
                 'account_id': account_id,
                 'text': text,
                 'offset': offset,
                 'limit': limit}

    tasks = [db.sql(sql_count, arguments),
             db.sql(sql, arguments)]

    count_results, messages_result = await asyncio.gather(*tasks)

    return count_results[0]['total'], [message_from_row(row) for row in messages_result]


async def get_data_report(account_id):
    data = []

    number, sent_messages = await load_messages(account_id,
                                                type=relations.OWNER_TYPE.SENDER,
                                                visibility=None)

    number, received_messages = await load_messages(account_id,
                                                    type=relations.OWNER_TYPE.RECIPIENT,
                                                    visibility=None)

    for message in itertools.chain(sent_messages, received_messages):
        data.append(('message', message.data_of(account_id)))

    return data


async def clean_messages():
    await db.sql('TRUNCATE visibilities, conversations, messages, accounts')
