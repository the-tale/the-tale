
import asyncio

from aiohttp import web

from tt_web import log
from tt_web import postgresql


async def initialize(config, loop):
    await postgresql.initialize(config['database'], loop=loop)


async def deinitialize(config, loop):
    await postgresql.deinitialize()


async def on_startup(app):
    await initialize(app['config'], loop=app.loop)


async def on_cleanup(app):
    await deinitialize(app['config'], loop=app.loop)


def register_routers(app):
    from . import handlers

    app.router.add_post('/accounts/balance', handlers.account_balance)
    app.router.add_post('/accounts/history', handlers.account_history)

    app.router.add_post('/transactions/start', handlers.start_transaction)
    app.router.add_post('/transactions/commit', handlers.commit_transaction)
    app.router.add_post('/transactions/rollback', handlers.rollback_transaction)

    app.router.add_post('/debug-clear-service', handlers.debug_clear_service)


def create_application(config, loop=None):
    app = web.Application(loop=loop)

    app['config'] = config

    log.initilize(config['log'])

    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)

    register_routers(app)

    return app


def run_utility(config, utility):
    loop = asyncio.get_event_loop()

    async def runner():
        await initialize(config, loop=loop)

        log.initilize(config['log'])

        await utility(loop=loop)

        await deinitialize(config, loop=loop)

    loop.run_until_complete(runner())
