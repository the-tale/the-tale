

from tt_web import postgresql as db

from . import objects


def property_from_row(row):
    return objects.Property(object_id=row['object_id'],
                            type=row['property_type'],
                            value=row['value'])


async def set_properties(properties):

    for property in properties:
        await set_property(property)


async def set_property(property):

    result = await db.sql('''UPDATE properties
                             SET value=%(value)s,
                                 updated_at=NOW()
                             WHERE object_id=%(object_id)s AND property_type=%(type)s
                             RETURNING id''',
                          {'object_id': property.object_id,
                           'type': property.type,
                           'value': property.value})

    if result:
        return

    await db.sql('''INSERT INTO properties (object_id, property_type, value, created_at, updated_at)
                    VALUES (%(object_id)s, %(type)s, %(value)s, NOW(), NOW())
                    ON CONFLICT (object_id, property_type) DO UPDATE SET value = EXCLUDED.value''',
                 {'object_id': property.object_id,
                  'type': property.type,
                  'value': property.value})


async def get_properties(objects):
    properties = []

    for object_id, types in objects.items():
        properties.extend(await get_object_properties(object_id, types))

    return properties


async def get_object_properties(object_id, types):
    if not types:
        return {object_id: []}

    result = await db.sql('''SELECT object_id, property_type, value FROM properties
                             WHERE object_id=%(object_id)s AND property_type IN %(types)s''',
                          {'object_id': object_id,
                           'types': tuple(types)})

    return [property_from_row(row) for row in result]


async def clean_database():
    await db.sql('TRUNCATE properties')
