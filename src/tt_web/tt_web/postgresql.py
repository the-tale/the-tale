
import aiopg
import psycopg2


POOL = None

DSN = 'dbname={dbname} user={user} password={password} host={host} port={port}'


async def initialize(config, loop=None):
    global POOL

    POOL = await  aiopg.create_pool(dsn=DSN.format(dbname=config['name'],
                                                   user=config['user'],
                                                   password=config['password'],
                                                   host=config['host'],
                                                   port=config['port']),
                                    minsize=config['minsize'],
                                    maxsize=config['maxsize'],
                                    timeout=config['timeout'],
                                    loop=loop)


async def deinitialize():
    POOL.close()
    await POOL.wait_closed()


async def execute(cursor, command, arguments):
    await cursor.execute(command, arguments)
    try:
        result = await cursor.fetchall()
    except psycopg2.ProgrammingError:
        result = None
    return result


async def sql(command, arguments=None):
    async with POOL.acquire() as connection:
        async with connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            return await execute(cursor, command, arguments)


async def transaction(callback, arguments):
    async with POOL.acquire() as connection:
        async with connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:

            await cursor.execute('BEGIN')

            try:
                result = await callback(arguments=arguments,
                                        execute=lambda command, arguments=None: execute(cursor, command, arguments))
            except:
                await cursor.execute('ROLLBACK')
                raise
            else:
                await cursor.execute('COMMIT')

            return result
