

from psycopg2.extras import Json as PGJson

from tt_web import postgresql as db

from . import objects


def effect_data(effect):
    return {'value': effect.value,
            'caption': effect.caption,
            'data': effect.data}


def effect_from_row(row):
    return objects.Effect(id=row['id'],
                          attribute=row['attribute'],
                          entity=row['entity'],
                          value=row['data']['value'],
                          caption=row['data']['caption'],
                          data=row['data']['data'])


async def register_effect(effect):

    results = await db.sql('''INSERT INTO effects (attribute, entity, data, created_at, updated_at)
                              VALUES (%(attribute)s, %(entity)s, %(data)s, NOW(), NOW())
                              RETURNING id''',
                           {'attribute': effect.attribute,
                            'entity': effect.entity,
                            'data': PGJson(effect_data(effect))})

    return results[0]['id']


async def remove_effect(effect_id):
    await db.sql('DELETE FROM effects WHERE id=%(effect_id)s',
                 {'effect_id': effect_id})


async def update_effect(effect):
    results = await db.sql('''UPDATE effects
                              SET attribute=%(attribute)s,
                                  entity=%(entity)s,
                                  data=%(data)s,
                                  updated_at=NOW()
                              WHERE id=%(id)s
                              RETURNING id''',
                           {'id': effect.id,
                            'attribute': effect.attribute,
                            'entity': effect.entity,
                            'data': PGJson(effect_data(effect))})

    return bool(results)


async def load_effects():
    results = await db.sql('SELECT * FROM effects ORDER BY created_at')

    return [effect_from_row(row) for row in results]


async def clean_database():
    await db.sql('TRUNCATE effects')
