

from tt_web import postgresql as db

from . import objects
from . import relations


def property_from_row(row):
    return objects.Property(object_id=row['object_id'],
                            type=row['property_type'],
                            value=row['value'],
                            mode=relations.MODE.UNKNOWN)


async def set_properties(properties):

    for property in properties:
        if property.mode == relations.MODE.REPLACE:
            await set_property(property)
        elif property.mode == relations.MODE.APPEND:
            await append_property(property)
        else:
            raise NotImplementedError('unknowm property mode')


async def set_property(property):
    await db.sql('DELETE FROM properties WHERE object_id=%(object_id)s AND property_type=%(type)s',
                 {'object_id': property.object_id,
                  'type': property.type})

    await db.sql('''INSERT INTO properties (object_id, property_type, value, created_at)
                    VALUES (%(object_id)s, %(type)s, %(value)s, NOW())''',
                 {'object_id': property.object_id,
                  'type': property.type,
                  'value': property.value})


async def append_property(property):
    await db.sql('''INSERT INTO properties (object_id, property_type, value, created_at)
                    VALUES (%(object_id)s, %(type)s, %(value)s, NOW())''',
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
                             WHERE object_id=%(object_id)s AND property_type IN %(types)s
                             ORDER BY created_at''',  # guaranty created order, if multiple properties extracted
                          {'object_id': object_id,
                           'types': tuple(types)})

    return [property_from_row(row) for row in result]


async def get_data_report(object_id):
    data = []

    result = await db.sql('''SELECT object_id, property_type, value FROM properties
                             WHERE object_id=%(object_id)s
                             ORDER BY created_at''',  # guaranty created order, if multiple properties extracted
                          {'object_id': object_id})

    for row in result:
        property = property_from_row(row)
        data.append(('property', {'type': property.type,
                                  'value': property.value}))

    return data


async def clean_object_properties(object_id):
    await db.sql('DELETE FROM properties WHERE object_id=%(object_id)s',
                 {'object_id': object_id})


async def clean_database():
    await db.sql('TRUNCATE properties')
