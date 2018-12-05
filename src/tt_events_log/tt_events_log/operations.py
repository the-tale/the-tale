
from psycopg2.extras import Json as PGJson

from tt_web import postgresql as db

from . import objects


def event_from_row(row):
    return objects.Event(id=row['id'],
                         tags=set(),
                         data=row['data'],
                         created_at=row['created_at'],
                         created_at_turn=row['created_at_turn'])


async def add_event(tags, data, turn, time):
    return await db.transaction(_add_event, {'tags': tags,
                                             'data': data,
                                             'turn': turn,
                                             'time': time})


async def _add_event(execute, arguments):
    tags = arguments['tags']
    data = arguments['data']
    turn = arguments['turn']
    time = arguments['time']

    result = await execute('''INSERT INTO events (data, created_at, created_at_turn)
                              VALUES (%(data)s, %(time)s, %(turn)s)
                              RETURNING id''',
                           {'data': PGJson(data),
                            'time': time,
                            'turn': turn})

    event_id = result[0]['id']

    for tag in tags:
        await execute('''INSERT INTO events_tags (event, tag, created_at, created_at_turn)
                         VALUES (%(event)s, %(tag)s, %(time)s, %(turn)s)''',
                      {'event': event_id,
                       'tag': tag,
                       'time': time,
                       'turn': turn})

    return event_id


async def events_number(tags):
    if not tags:
        result = await db.sql('SELECT count(*) as events_number FROM events')

    else:
        result = await db.sql('''SELECT count(*) as events_number
                                 FROM (SELECT event FROM events_tags
                                       WHERE tag IN %(tags)s
                                       GROUP BY event
                                       HAVING count(*) = %(tags_number)s) as filtered_events''',
                              {'tags_number': len(tags),
                               'tags': tuple(tags)})

    return result[0]['events_number']


async def _process_get_all(result):
    events = [event_from_row(row) for row in result]

    await fill_events_with_tags(events)

    return events


async def get_all_events(page, records_on_page):
    result = await db.sql('SELECT * FROM events ORDER BY created_at ASC, created_at_turn ASC OFFSET %(offset)s LIMIT %(limit)s',
                          {'offset': (page - 1) * records_on_page,
                           'limit': records_on_page})

    return await _process_get_all(result)


async def get_all_last_events(number):
    result = await db.sql('SELECT * FROM events ORDER BY created_at DESC, created_at_turn DESC LIMIT %(limit)s',
                          {'limit': number})

    return await _process_get_all(reversed(result))


async def _process_get_by_tags(result):

    if not result:
        return []

    events_ids = tuple(row['event'] for row in result)

    result = await db.sql('SELECT * FROM events WHERE id IN %(ids)s ORDER BY created_at ASC, created_at_turn ASC',
                          {'ids': events_ids})

    events = [event_from_row(row) for row in result]

    await fill_events_with_tags(events)

    return events


async def get_events_by_tags(tags, page, records_on_page):
    result = await db.sql('''SELECT event, MIN(created_at) as created_at, MIN(created_at_turn) as created_at_turn FROM events_tags
                             WHERE tag IN %(tags)s
                             GROUP BY event
                             HAVING count(*) = %(tags_number)s
                             ORDER BY created_at ASC, created_at_turn ASC
                             OFFSET %(offset)s
                             LIMIT %(limit)s''',
                          {'tags_number': len(tags),
                           'tags': tuple(tags),
                           'offset': (page - 1) * records_on_page,
                           'limit': records_on_page})

    return await _process_get_by_tags(result)


async def get_last_events_by_tags(tags, number):
    result = await db.sql('''SELECT event, MIN(created_at) as created_at, MIN(created_at_turn) as created_at_turn FROM events_tags
                             WHERE tag IN %(tags)s
                             GROUP BY event
                             HAVING count(*) = %(tags_number)s
                             ORDER BY created_at DESC, created_at_turn DESC
                             LIMIT %(limit)s''',
                          {'tags_number': len(tags),
                           'tags': tuple(tags),
                           'limit': number})

    return await _process_get_by_tags(result)


async def fill_events_with_tags(events):
    if not events:
        return

    events_by_id = {event.id: event for event in events}

    result = await db.sql('SELECT event, tag FROM events_tags WHERE event IN %(ids)s',
                          {'ids': tuple(event.id for event in events)})

    for row in result:
        events_by_id[row['event']].tags.add(row['tag'])


async def clean_database():
    await db.sql('TRUNCATE events_tags, events')
