
import logging

import psycopg2

from tt_web import postgresql as db

from . import objects
from . import exceptions


def battle_request_from_row(row):
    return objects.BattleRequest(id=row['id'],
                                 initiator_id=row['initiator'],
                                 matchmaker_type=row['matchmaker_type'],
                                 created_at=row['created_at'],
                                 updated_at=row['updated_at'])


def battle_from_row(row, participants_ids):
    return objects.Battle(id=row['id'],
                          matchmaker_type=row['matchmaker_type'],
                          participants_ids=participants_ids,
                          created_at=row['created_at'])


async def create_battle_request(matchmaker_type, initiator_id):
    result = await db.sql('''INSERT INTO battle_requests (initiator, matchmaker_type, created_at, updated_at)
                             VALUES (%(initiator_id)s, %(matchmaker_type)s, NOW(), NOW())
                             ON CONFLICT (matchmaker_type, initiator) DO UPDATE
                                SET updated_at=NOW()
                             RETURNING id''',
                          {'initiator_id': initiator_id,
                           'matchmaker_type': matchmaker_type})

    battle_request_id = result[0]['id']

    logging.info('battle request %s created, matchmaker_type=%s, initiator_id=%s', battle_request_id, matchmaker_type, initiator_id)

    return battle_request_id


async def cancel_battle_request(battle_request_id):
    await db.sql('DELETE FROM battle_requests WHERE id=%(id)s',
                 {'id': battle_request_id})

    logging.info('battle request %s canceled', battle_request_id)


async def load_battle_requests(battle_requests_ids):
    battle_requests = await db.sql('SELECT * FROM battle_requests WHERE id IN %(ids)s',
                                   {'ids': tuple(battle_requests_ids)})

    return [battle_request_from_row(row) for row in battle_requests]


async def list_battle_requests(matchmaker_types):
    battle_requests = await db.sql('SELECT * FROM battle_requests WHERE matchmaker_type IN %(matchmaker_types)s',
                                   {'matchmaker_types': tuple(matchmaker_types)})

    initiators = {row['initiator'] for row in battle_requests}

    result = await db.sql('SELECT participant FROM battles_participants')

    initiators -= {row['participant'] for row in result}

    return [battle_request_from_row(row) for row in battle_requests
            if row['initiator'] in initiators]


async def accept_battle_request(battle_request_id, acceptor_id):
    battle_id, participants_ids = await db.transaction(_accept_battle_request,
                                                       {'battle_request_id': battle_request_id,
                                                        'acceptor_id': acceptor_id})

    logging.info('battle request %s accepted, acceptor_id=%s, battle_id=%s, participants_ids=%s',
                 battle_request_id, acceptor_id, battle_id, participants_ids)

    return battle_id, participants_ids


async def _accept_battle_request(execute, arguments):
    battle_request_id = arguments['battle_request_id']
    acceptor_id = arguments['acceptor_id']

    result = await execute('SELECT * from battle_requests WHERE id=%(id)s',
                           {'id': battle_request_id})

    if not result:
        logging.warning('can not accept battle request %s: no request found', battle_request_id)
        raise exceptions.NoBattleRequestFound(battle_request=battle_request_id)

    initiator_id = result[0]['initiator']
    matchmaker_type = result[0]['matchmaker_type']

    participants_ids = (initiator_id, acceptor_id)

    battle_id = await _create_battle(execute, arguments={'matchmaker_type': matchmaker_type,
                                                         'participants_ids': participants_ids})

    return battle_id, participants_ids


async def create_battle(matchmaker_type, participants_ids):
    battle_id = await db.transaction(_create_battle, {'matchmaker_type': matchmaker_type,
                                                      'participants_ids': participants_ids})
    logging.info('battle  %s created, participants=%s', battle_id, participants_ids)

    return battle_id


async def _create_battle(execute, arguments):
    matchmaker_type = arguments['matchmaker_type']
    participants_ids = arguments['participants_ids']

    if len(participants_ids) != len(set(participants_ids)):
        logging.warning('duplicate battle participants, while createing battle, matchmaker_type=%s, participants_ids=%s',
                        matchmaker_type, participants_ids)
        raise exceptions.DuplicateBattleParticipants(participants=participants_ids)

    result = await execute('''INSERT INTO battles (matchmaker_type, created_at)
                              VALUES (%(matchmaker_type)s, NOW())
                              RETURNING id''',
                           {'matchmaker_type': matchmaker_type})

    battle_id = result[0]['id']

    # sort to improve detection of battle participants intersections
    participants_ids = list(sorted(participants_ids))

    for participant_id in participants_ids:
        try:
            await execute('''INSERT INTO battles_participants (battle, participant, created_at)
                             VALUES (%(battle_id)s, %(participant_id)s, NOW())''',
                          {'battle_id': battle_id,
                           'participant_id': participant_id})
        except psycopg2.IntegrityError:
            logging.warning('battle participants intersection while creating battle, matchmaker_type=%s, participants_ids=%s',
                            matchmaker_type, participants_ids)
            raise exceptions.BattleParticipantsIntersection(participant=participant_id)

    await execute('''DELETE FROM battle_requests
                     WHERE initiator IN %(initiators_ids)s''',
                  {'matchmaker_type': matchmaker_type,
                   'initiators_ids': tuple(participants_ids)})

    return battle_id


async def finish_battle(battle_id):
    await db.transaction(_finish_battle, {'battle_id': battle_id})

    logging.info('battle %s finished', battle_id)


async def _finish_battle(execute, arguments):
    battle_id = arguments['battle_id']

    await db.sql('DELETE FROM battles_participants WHERE battle=%(battle_id)s',
                 {'battle_id': battle_id})

    await db.sql('DELETE FROM battles WHERE id=%(id)s',
                 {'id': battle_id})


async def active_battles_number(matchmaker_types):
    result = await db.sql('''SELECT matchmaker_type, COUNT(*) as number FROM battles
                             WHERE matchmaker_type IN %(matchmaker_types)s
                             GROUP BY matchmaker_type''',
                          {'matchmaker_types': tuple(matchmaker_types)})

    battles_number = {row['matchmaker_type']: row['number'] for row in result}

    for matchmaker_type in matchmaker_types:
        if matchmaker_type not in battles_number:
            battles_number[matchmaker_type] = 0

    return battles_number


async def load_battles_by_participants(participants_ids):
    if not participants_ids:
        return []

    battles_rows = await db.sql('''SELECT * FROM battles
                                   WHERE id IN (SELECT DISTINCT ON (battle) battle FROM battles_participants
                                                WHERE participant IN %(participants_ids)s
                                                ORDER BY battle)''',
                                   {'participants_ids': tuple(participants_ids)})

    if not battles_rows:
        return []

    battles_ids = tuple(row['id'] for row in battles_rows)

    result = await db.sql('SELECT battle, participant FROM battles_participants WHERE battle IN %(battles_ids)s',
                          {'battles_ids': battles_ids})

    participants = {battle_id: [] for battle_id in battles_ids}

    for row in result:
        participants[row['battle']].append(row['participant'])

    return [battle_from_row(battle_row, participants_ids=participants[battle_row['id']])
            for battle_row in battles_rows]


async def clean_database():
    await db.sql('''TRUNCATE battle_requests,
                             battles,
                             battles_participants''')
