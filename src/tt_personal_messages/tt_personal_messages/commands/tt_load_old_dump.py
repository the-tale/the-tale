
import sys
import json

import logging
import argparse
import importlib
import datetime

import asyncio

from aiohttp import web

from tt_web import utils
from tt_web import postgresql as db

from tt_personal_messages import operations


parser = argparse.ArgumentParser(description='Run service')

parser.add_argument('-c', '--config', metavar='config', type=str, help='path to config file')


async def on_startup(config):
    await db.initialize(config['database'])


async def create_account(account):
    await db.sql('''INSERT INTO accounts (id, new_messages_number, created_at, updated_at)
                    VALUES (%(account_id)s, 0, %(created_at)s, %(created_at)s)''',
                 {'account_id': account['id'],
                  'created_at': datetime.datetime.fromtimestamp(account['created_at'])})


async def create_message(id, message):
    await db.sql('''INSERT INTO messages (id, sender, recipients, body, created_at, updated_at)
                    VALUES (%(id)s, %(sender)s, %(recipients)s, %(body)s, %(created_at)s, %(created_at)s)
                    RETURNING id''',
                 {'id': id,
                  'sender': message['sender_id'],
                  'recipients': message['recipients_ids'],
                  'body': message['body'],
                  'created_at': datetime.datetime.fromtimestamp(message['created_at'])})


async def create_visibility(v):
    await db.sql('''INSERT INTO visibilities (account, message, visible, created_at, updated_at)
                    VALUES (%(account)s, %(message)s, %(visible)s, %(created_at)s, %(created_at)s)''',
                 {'account': v['account_id'],
                  'message': v['message_id'],
                  'visible': v['visible'],
                  'created_at': datetime.datetime.fromtimestamp(v['created_at']),})


async def create_conversation(c):
    await db.sql('''INSERT INTO conversations (account_1, account_2, message, created_at, updated_at)
                    VALUES (%(account_1)s, %(account_2)s, %(message)s, %(created_at)s, %(created_at)s)''',
                 {'account_1': c['account_1'],
                  'account_2': c['account_2'],
                  'message': c['message_id'],
                  'created_at': datetime.datetime.fromtimestamp(c['created_at']),})



def chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]


async def run_command():
    args = parser.parse_args()

    config = utils.load_config(args.config)

    data = json.loads(sys.stdin.read())

    await on_startup(config)

    await operations.clean_messages()

    print('create accounts')
    tasks = []

    for account in data['accounts'].values():
        tasks.append(create_account(account))

    await asyncio.gather(*tasks)

    print('create messages')
    tasks = []

    for i, message in enumerate(data['messages'], 1):
        tasks.append(create_message(i, message))

    await asyncio.gather(*tasks)

    print('create visibilities')

    for vs in chunks(data['visibilities'], 100):
        tasks = []
        for v in vs:
            tasks.append(create_visibility(v))

        await asyncio.gather(*tasks)

    print('create conversations')

    for cs in chunks(data['conversations'], 100):
        tasks = []
        for c in cs:
            tasks.append(create_conversation(c))

        await asyncio.gather(*tasks)

    await db.sql('ALTER SEQUENCE messages_id_seq RESTART WITH {}'.format(len(data['messages'])+1))

    asyncio.get_event_loop().stop()


def main():
    asyncio.get_event_loop().create_task(run_command())
    asyncio.get_event_loop().run_forever()
