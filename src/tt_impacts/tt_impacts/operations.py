
import asyncio

from tt_web import postgresql as db

from . import logic
from . import objects


def impact_from_row(row):
    return objects.Impact(transaction=row['transaction'],
                          actor=objects.Object(row['actor_type'], row['actor']),
                          target=objects.Object(row['target_type'], row['target']),
                          amount=row['amount'],
                          turn=row['created_at_turn'],
                          time=row['created_at'].replace(tzinfo=None))


def actor_impact_from_row(row):
    return objects.ActorImpact(actor=objects.Object(row['actor_type'], row['actor']),
                               target=objects.Object(row['target_type'], row['target']),
                               amount=row['amount'],
                               turn=row['updated_at_turn'],
                               time=row['updated_at'].replace(tzinfo=None))


def target_impact_from_row(row):
    return objects.TargetImpact(target=objects.Object(row['target_type'], row['target']),
                                amount=row['amount'],
                                turn=row['updated_at_turn'],
                                time=row['updated_at'].replace(tzinfo=None))


async def add_impacts(impacts):
    await db.transaction(_add_impacts, {'impacts': impacts})


async def _add_impacts(execute, arguments):
    # order of executed queries and sorting of items in quiries
    # required to prevent blocking with add_impacts and scale_impacts functions

    impacts = list(arguments['impacts'])

    for impact in impacts:
        await _add_impact(execute, impact)

    impacts.sort(key=lambda impact: (impact.actor.type, impact.actor.id, impact.target.type, impact.target.id))

    for impact in impacts:
        await _add_actor_impact(execute, impact)

    impacts.sort(key=lambda impact: (impact.target.type, impact.target.id))

    for impact in impacts:
        await _add_target_impact(execute, impact)


async def _add_impact(execute, impact):
    sql = '''INSERT INTO impacts (actor_type, actor, target_type, target, amount, transaction, created_at_turn, created_at)
             VALUES (%(actor_type)s, %(actor)s, %(target_type)s, %(target)s, %(amount)s, %(transaction)s, %(turn)s, NOW())'''

    await execute(sql, {'actor_type': impact.actor.type,
                        'actor': impact.actor.id,
                        'target_type': impact.target.type,
                        'target': impact.target.id,
                        'amount': impact.amount,
                        'transaction': impact.transaction,
                        'turn': impact.turn})


async def _add_actor_impact(execute, impact):
    sql = '''INSERT INTO actors_impacts (actor_type, actor, target_type, target, amount, created_at, updated_at, updated_at_turn)
             VALUES (%(actor_type)s, %(actor)s, %(target_type)s, %(target)s, %(amount)s, NOW(), NOW(), %(turn)s)
             ON CONFLICT (actor_type, actor, target_type, target) DO UPDATE
             SET amount = actors_impacts.amount + %(amount)s,
                 updated_at = GREATEST(actors_impacts.updated_at, NOW()),
                 updated_at_turn = GREATEST(actors_impacts.updated_at_turn, %(turn)s)'''

    await execute(sql, {'actor_type': impact.actor.type,
                        'actor': impact.actor.id,
                        'target_type': impact.target.type,
                        'target': impact.target.id,
                        'amount': impact.amount,
                        'turn': impact.turn})

async def _add_target_impact(execute, impact):
    sql = '''INSERT INTO targets_impacts (target_type, target, amount, created_at, updated_at, updated_at_turn)
             VALUES (%(target_type)s, %(target)s, %(amount)s, NOW(), NOW(), %(turn)s)
             ON CONFLICT (target_type, target) DO UPDATE
             SET amount = targets_impacts.amount + %(amount)s,
                 updated_at = GREATEST(targets_impacts.updated_at, NOW()),
                 updated_at_turn = GREATEST(targets_impacts.updated_at_turn, %(turn)s)'''

    await execute(sql, {'target_type': impact.target.type,
                        'target': impact.target.id,
                        'amount': impact.amount,
                        'turn': impact.turn})


async def last_impacts(limit):
    results = await db.sql('SELECT * FROM impacts ORDER BY created_at DESC LIMIT %(limit)s', {'limit': limit})
    return [impact_from_row(row) for row in results]


async def last_actor_impacts(actor, limit):
    results = await db.sql('''SELECT * FROM impacts
                              WHERE actor_type=%(actor_type)s AND actor=%(actor)s
                              ORDER BY created_at DESC LIMIT %(limit)s''',
                           {'limit': limit,
                            'actor_type': actor.type,
                            'actor': actor.id})
    return [impact_from_row(row) for row in results]


async def last_target_impacts(target, limit):
    results = await db.sql('''SELECT * FROM impacts
                              WHERE target_type=%(target_type)s AND target=%(target)s
                              ORDER BY created_at DESC LIMIT %(limit)s''',
                           {'limit': limit,
                            'target_type': target.type,
                            'target': target.id})
    return [impact_from_row(row) for row in results]


async def last_actor_target_impacts(actor, target, limit):
    results = await db.sql('''SELECT * FROM impacts
                              WHERE actor_type=%(actor_type)s AND
                                    actor=%(actor)s AND
                                    target_type=%(target_type)s AND
                                    target=%(target)s
                              ORDER BY created_at DESC LIMIT %(limit)s''',
                           {'limit': limit,
                            'actor_type': actor.type,
                            'actor': actor.id,
                            'target_type': target.type,
                            'target': target.id})
    return [impact_from_row(row) for row in results]


async def get_targets_impacts(targets):
    sql = 'SELECT * FROM targets_impacts WHERE {conditions}'

    conditions = []

    for target in targets:
        conditions.append('(target_type={} AND target={})'.format(target.type, target.id))

    sql = sql.format(conditions=' OR '.join(conditions) if conditions else 'TRUE')

    results = await db.sql(sql)

    return [target_impact_from_row(row) for row in results]


async def get_impacters_ratings(targets, actor_types, limit):

    if not targets:
        return {}

    if not actor_types:
        return {}

    targets = frozenset(targets)

    tasks = [get_impacters_target_ratings(target, actor_types, limit) for target in targets]

    done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_EXCEPTION)

    return dict(task.result() for task in done)


async def get_actor_impacts(actor, target_types):
    sql = '''SELECT * FROM actors_impacts
             WHERE actor_type = %(actor_type)s AND
                   actor = %(actor_id)s AND
                   target_type IN %(target_types)s'''

    results = await db.sql(sql, {'actor_type': actor.type,
                                 'actor_id': actor.id,
                                 'target_types': tuple(target_types)})

    return [target_impact_from_row(row) for row in results]


async def get_impacters_target_ratings(target, actor_types, limit):
    sql = '''SELECT * FROM actors_impacts
             WHERE actor_type IN %(actor_types)s AND
                   target_type = %(target_type)s AND
                   target = %(target_id)s
             ORDER BY amount DESC LIMIT %(limit)s'''

    results = await db.sql(sql, {'target_type': target.type,
                                 'target_id': target.id,
                                 'actor_types': tuple(actor_types),
                                 'limit': limit})

    return target, [actor_impact_from_row(row) for row in results]


async def scale_impacts(target_types, scale, chunk_size):
    if not target_types:
        return

    await db.transaction(_scale_impacts, {'target_types': target_types,
                                          'scale': scale,
                                          'chunk_size': chunk_size})


async def _scale_impacts(execute, arguments):
    target_types = tuple(arguments['target_types'])
    scale = arguments['scale']
    chunk_size = arguments['chunk_size']

    # order of executed queries and sorting of items in quiries
    # required to prevent blocking with add_impacts and scale_impacts functions

    results = await execute('''SELECT id FROM actors_impacts
                               WHERE target_type IN %(target_types)s
                               ORDER BY (actor_type, actor, target_type, target)''',
                            {'target_types': target_types})

    actor_impacts_ids = [row['id'] for row in results]

    for ids in logic.chunks(actor_impacts_ids, chunk_size):
        await execute('''UPDATE actors_impacts
                         SET amount =
                             CASE
                                 WHEN amount < 0 THEN CEIL(amount * %(scale)s)
                                 ELSE FLOOR(amount * %(scale)s)
                             END
                          WHERE id IN %(ids)s''',
                      {'ids': tuple(ids),
                       'scale': scale})

    results = await execute('''SELECT id FROM targets_impacts
                               WHERE target_type IN %(target_types)s
                               ORDER BY (target_type, target)''',
                            {'target_types': target_types})

    targets_impacts_ids = [row['id'] for row in results]

    for ids in logic.chunks(targets_impacts_ids, chunk_size):
        await execute('''UPDATE targets_impacts
                         SET amount =
                             CASE
                                 WHEN amount < 0 THEN CEIL(amount * %(scale)s)
                                 ELSE FLOOR(amount * %(scale)s)
                             END
                         WHERE id IN %(ids)s''',
                      {'ids': tuple(ids),
                       'scale': scale})


async def clean_database():
    await db.sql('TRUNCATE targets_impacts, actors_impacts, impacts')
