
from psycopg2.extras import Json as PGJson

from tt_web import postgresql as db
from tt_web import utils

from . import objects


TIMESTAMPS_CACHE = {}


CHANGE_DIARY_POINT = utils.SyncPoint()


async def initialize_timestamps_cache():
    results = await db.sql('SELECT id, version FROM diaries')
    TIMESTAMPS_CACHE.update({row['id']: row['version'] for row in results})


async def push_message(account_id, message, diary_size):
    async with CHANGE_DIARY_POINT.lock(account_id):
        diary = await load_diary(account_id)

        if diary is None:
            diary = objects.Diary()

        diary.push_message(message, diary_size=diary_size)
        await save_diary(account_id, diary)


async def load_diary(account_id):

    result = await db.sql('SELECT data, version FROM diaries WHERE id=%(account_id)s', {'account_id': account_id})

    if not result:
        return None

    diary = objects.Diary()

    for message_data in result[0]['data']['messages']:
        diary.push_message(objects.Message.deserialize(message_data), increment_version=False)

    diary.version = result[0]['version']

    return diary


async def save_diary(account_id, diary):

    sql = '''INSERT INTO diaries (id, data, created_at, updated_at, version)
             VALUES (%(account_id)s, %(data)s, NOW(), NOW(), %(version)s)
             ON CONFLICT (id) DO UPDATE SET data=EXCLUDED.data, version=EXCLUDED.version, updated_at=EXCLUDED.updated_at
             RETURNING version'''

    data = {'messages': [message.serialize() for message in diary.messages()]}

    result = await db.sql(sql, {'account_id': account_id, 'data': PGJson(data), 'version': diary.version})

    TIMESTAMPS_CACHE[account_id] = result[0]['version']


async def clean_diaries():
    await db.sql('TRUNCATE diaries')


async def count_diaries():
    results = await db.sql('SELECT count(*) FROM diaries')
    return results[0][0]
