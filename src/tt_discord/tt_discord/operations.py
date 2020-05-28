
import uuid
import logging

from psycopg2.extras import Json as PGJson

from tt_web import postgresql as db
from tt_web.common import event

from . import conf
from . import objects
from . import relations


def row_to_account_info(row):
    return objects.AccountInfo(id=row['id'],
                               game_id=row['game_id'],
                               discord_id=row['discord_id'])


async def create_account(game_id=None, discord_id=None, execute=db.sql):

    if game_id is not None and discord_id is not None:
        raise NotImplementedError

    result = await execute('''INSERT INTO accounts (discord_id, game_id, created_at, updated_at)
                              VALUES (%(discord_id)s, %(game_id)s, NOW(), NOW())
                              ON CONFLICT DO NOTHING
                              RETURNING *''',
                           {'game_id': game_id,
                            'discord_id': discord_id})

    if result:
        return row_to_account_info(result[0])

    if game_id is not None:
        return await get_account_info_by_game_id(game_id, create_if_not_exists=False)

    return await get_account_info_by_discord_id(discord_id)


async def get_account_info_by_game_id(game_id, create_if_not_exists):

    result = await db.sql('SELECT * FROM accounts WHERE game_id=%(game_id)s',
                          {'game_id': game_id})

    if result:
        return row_to_account_info(result[0])

    if create_if_not_exists:
        return await create_account(game_id)

    return objects.AccountInfo(id=None,
                               game_id=game_id,
                               discord_id=None)


async def get_account_info_by_discord_id(discord_id):

    result = await db.sql('SELECT * FROM accounts WHERE discord_id=%(discord_id)s',
                          {'discord_id': discord_id})

    if result:
        return row_to_account_info(result[0])

    return objects.AccountInfo(id=None,
                               game_id=None,
                               discord_id=discord_id)


async def get_account_info_by_id(account_id):

    result = await db.sql('SELECT * FROM accounts WHERE id=%(account_id)s',
                          {'account_id': account_id})

    if result:
        return row_to_account_info(result[0])

    return objects.AccountInfo(id=None,
                               game_id=None,
                               discord_id=None)


async def _update_game_data(account_id, type, data, force, logger, execute=db.sql):

    # TODO: rewrite not best solution of comparing json data

    logger.info('try to update account %s %s with data %s (force: %s)', account_id, type, data, force)

    result = await execute('''INSERT INTO game_data (account, type, data, created_at, updated_at, synced_at)
                              VALUES (%(account_id)s, %(type)s, %(data)s, NOW(), NOW(), NULL)
                              ON CONFLICT (account, type) DO UPDATE SET data=EXCLUDED.data,
                                                                        updated_at=NOW()
                                                                    WHERE %(force)s OR game_data.data<>EXCLUDED.data
                              RETURNING account''',
                           {'account_id': account_id,
                            'data': PGJson(data),
                            'type': type.value,
                            'force': force})

    if result:
        event.get(conf.SYNC_EVENT_NAME).set()


async def update_game_data(account_id, force=False, execute=db.sql, logger=logging, **kwargs):

    if 'nickname' in kwargs:
        await _update_game_data(account_id,
                                type=relations.GAME_DATA_TYPE.NICKNAME,
                                data={'nickname': kwargs['nickname']},
                                force=force,
                                logger=logger,
                                execute=execute)

    if 'roles' in kwargs:
        await _update_game_data(account_id,
                                type=relations.GAME_DATA_TYPE.ROLES,
                                data={'roles': sorted(kwargs['roles'])},
                                force=force,
                                logger=logger,
                                execute=execute)

    if 'ban' in kwargs:
        await _update_game_data(account_id,
                                type=relations.GAME_DATA_TYPE.BAN,
                                data={'ban': kwargs['ban']},
                                force=force,
                                logger=logger,
                                execute=execute)


async def force_game_data_update(account_id):
    result = await db.sql('UPDATE game_data SET synced_at=NULL WHERE account=%(account_id)s RETURNING id',
                          {'account_id': account_id})

    if result:
        event.get(conf.SYNC_EVENT_NAME).set()


def row_to_changes(row):
    return {'account_id': row['account'],
            'type': relations.GAME_DATA_TYPE(row['type']),
            'data': row['data'],
            'updated_at': row['updated_at']}


async def get_new_game_data(account_id):

    result = await db.sql('''SELECT account, type, data, updated_at FROM game_data
                             WHERE account=%(account_id)s AND
                                   (synced_at IS NULL OR synced_at < updated_at)''',
                          {'account_id': account_id})

    return [row_to_changes(row) for row in result]


async def get_any_new_game_data(limit):

    result = await db.sql('''SELECT account, type, data, game_data.updated_at, synced_at FROM game_data
                             JOIN accounts ON accounts.id = game_data.account
                             WHERE discord_id IS NOT NULL AND (synced_at IS NULL OR synced_at < game_data.updated_at)
                             LIMIT %(limit)s''',
                          {'limit': limit})

    return [row_to_changes(row) for row in result]


async def mark_game_data_synced(account_id, type, synced_at):

    await db.sql('UPDATE game_data SET synced_at=%(synced_at)s WHERE account=%(account_id)s AND type=%(type)s',
                 {'synced_at': synced_at,
                  'account_id': account_id,
                  'type': type.value})


def row_to_bind_code(row):
    return objects.BindCode(code=row['code'],
                            created_at=row['created_at'],
                            expire_at=row['expire_at'])


async def get_bind_code(account_id, expire_timeout):

    result = await db.sql('''INSERT INTO bind_codes (code, account, created_at, expire_at)
                             VALUES (%(code)s, %(account_id)s, NOW(), NOW() + %(expire_timeout)s * INTERVAL '1 second')
                             ON CONFLICT (account) DO UPDATE SET code=%(code)s,
                                                                 created_at=NOW(),
                                                                 expire_at=NOW() + %(expire_timeout)s * INTERVAL '1 second'
                             RETURNING code, created_at, expire_at''',
                          {'account_id': account_id,
                           'expire_timeout': expire_timeout,
                           'code': uuid.uuid4()})

    return row_to_bind_code(result[0])


async def bind_discord_user(bind_code, discord_id):

    result = await db.transaction(_bind_discord_user, {'bind_code': bind_code,
                                                       'discord_id': discord_id})

    if result.is_success():
        event.get(conf.SYNC_EVENT_NAME).set()

    return result


async def _bind_discord_user(execute, arguments):
    bind_code = arguments['bind_code']
    new_discord_id = arguments['discord_id']

    result = await execute('SELECT * FROM bind_codes WHERE code=%(code)s FOR UPDATE',
                           {'code': bind_code})

    if not result:
        return relations.BIND_RESULT.CODE_NOT_FOUND

    code = row_to_bind_code(result[0])

    if code.is_expired():
        return relations.BIND_RESULT.CODE_EXPIRED

    await execute('UPDATE bind_codes SET expire_at=NOW() WHERE code=%(code)s',
                  {'code': bind_code})

    account_id = result[0]['account']

    result = await execute('SELECT discord_id FROM accounts WHERE id=%(account_id)s',
                           {'account_id': account_id})

    old_discord_id = result[0]['discord_id']

    if old_discord_id == new_discord_id:
        return relations.BIND_RESULT.ALREADY_BINDED

    await execute('UPDATE accounts SET discord_id=NULL, updated_at=NOW() WHERE discord_id=%(discord_id)s',
                  {'discord_id': new_discord_id})

    await execute('UPDATE accounts SET discord_id=%(discord_id)s, updated_at=NOW() WHERE id=%(account_id)s',
                  {'account_id': account_id,
                   'discord_id': new_discord_id})

    if old_discord_id is None:
        return relations.BIND_RESULT.SUCCESS_NEW

    await force_game_data_update(account_id)

    await create_account(game_id=None, discord_id=old_discord_id, execute=execute)

    return relations.BIND_RESULT.SUCCESS_REBIND


async def unbind_discord_user(discord_id):
    return await db.transaction(_unbind_discord_user, {'discord_id': discord_id})


async def _unbind_discord_user(execute, arguments):
    discord_id = arguments['discord_id']

    result = await execute('UPDATE accounts SET game_id=NULL, updated_at=NOW() WHERE discord_id=%(discord_id)s RETURNING id',
                           {'discord_id': discord_id})

    if not result:
        return

    await update_game_data(account_id=result[0]['id'],
                           nickname=None,
                           roles=[],
                           force=True,
                           execute=execute)

    event.get(conf.SYNC_EVENT_NAME).set()


async def get_orphan_discord_accounts():
    result = await db.sql('SELECT * FROM accounts WHERE discord_id IS NOT NULL and game_id IS NULL')

    return [row_to_account_info(row) for row in result]


async def delete_account(account_id):
    return await db.transaction(_delete_account, {'account_id': account_id})


async def _delete_account(execute, arguments):
    account_id = arguments['account_id']

    await execute('DELETE FROM game_data WHERE account=%(account_id)s',
                  {'account_id': account_id})

    await execute('DELETE FROM bind_codes WHERE account=%(account_id)s',
                  {'account_id': account_id})

    await execute('DELETE FROM accounts WHERE id=%(account_id)s',
                  {'account_id': account_id})


async def get_data_report(account_info):
    data = []

    if account_info.discord_id is not None:
        data.append(('discord_id', account_info.discord_id))

    if account_info.id:
        result = await db.sql('SELECT * FROM bind_codes WHERE account=%(account_id)s', {'account_id': account_info.id})

        for row in result:
            code = row_to_bind_code(row)
            data.append(('bind_code', code.data()))

    return data


async def clean_database():
    await db.sql('TRUNCATE accounts, game_data, bind_codes')
