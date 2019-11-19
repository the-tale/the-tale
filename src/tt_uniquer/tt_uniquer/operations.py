
from tt_web import postgresql as db


_CACHE = {}


def clear_cache():
    _CACHE.clear()


async def get_id(key):

    if key in _CACHE:
        return _CACHE[key]

    results = await db.sql('''INSERT INTO unique_ids (key, created_at, updated_at)
                              VALUES (%(key)s, NOW(), NOW())
                              ON CONFLICT (key) DO UPDATE SET updated_at = NOW()
                              RETURNING id''',
                           {'key': key})

    unique_id = results[0]['id']

    _CACHE[key] = unique_id

    return unique_id


async def clean_database():
    _CACHE.clear()
    await db.sql('TRUNCATE unique_ids')
