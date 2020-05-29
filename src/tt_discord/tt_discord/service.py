
import asyncio
import logging

from aiohttp import web

from tt_web import log
from tt_web import postgresql
from tt_web.common import event

from . import bot
from . import conf
from . import logic


DISCORD_BOT = None
DISCORD_BOT_TASK = None
DISCORD_SYNC_USERS_TASK = None


async def start_bot(config):
    global DISCORD_BOT
    global DISCORD_BOT_TASK
    global DISCORD_SYNC_USERS_TASK

    DISCORD_BOT = bot.construct(config)

    async def runner():
        await DISCORD_BOT.start(config['token'], bot=True, reconnect=True)

    DISCORD_BOT_TASK = asyncio.ensure_future(runner())

    async def update_users():
        event.get(conf.SYNC_EVENT_NAME).set()

        while True:
            try:
                await logic.sync_users(DISCORD_BOT, config)
            except Exception:
                logging.exception('error in user synchonisation task, sleep and continue')
                await asyncio.sleep(config['sleep_on_sync_users_error'])

    DISCORD_SYNC_USERS_TASK = asyncio.ensure_future(update_users())


async def stop_bot():
    global DISCORD_BOT
    global DISCORD_BOT_TASK
    global DISCORD_SYNC_USERS_TASK

    if DISCORD_BOT is None:
        return

    await DISCORD_BOT.close()

    DISCORD_BOT = None
    DISCORD_BOT_TASK = None

    if DISCORD_SYNC_USERS_TASK:
        DISCORD_SYNC_USERS_TASK.cancel()

    DISCORD_SYNC_USERS_TASK = None


async def on_startup(app):
    await postgresql.initialize(app['config']['database'])

    if (app['config']['custom']['discord']['connect_to_server']):
        logging.info('connect bot to discord')
        await start_bot(app['config']['custom']['discord'])
    else:
        logging.info('do not connect bot to discord')


async def on_cleanup(app):
    await postgresql.deinitialize()

    await stop_bot()


def register_routers(app):
    from . import handlers

    app.router.add_post('/get-bind-code', handlers.get_bind_code)
    app.router.add_post('/update-user', handlers.update_user)

    app.router.add_post('/data-protection-collect-data', handlers.data_protection_collect_data)
    app.router.add_post('/data-protection-delete-data', handlers.data_protection_delete_data)

    app.router.add_post('/debug-clear-service', handlers.debug_clear_service)


def create_application(config, loop=None):
    app = web.Application()

    app['config'] = config

    log.initilize(config['log'])

    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)

    register_routers(app)

    return app
