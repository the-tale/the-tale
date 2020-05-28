
import asyncio

from aiohttp import web

from tt_web import log
from tt_web import postgresql


async def initialize(config):
    await postgresql.initialize(config['database'])


async def deinitialize(config):
    await postgresql.deinitialize()


async def on_startup(app):
    await initialize(app['config'])


async def on_cleanup(app):
    await deinitialize(app['config'])


def register_routers(app):
    from . import handlers

    app.router.add_post('/request-report', handlers.request_report)
    app.router.add_post('/get-report', handlers.get_report)
    app.router.add_post('/request-deletion', handlers.request_deletion)

    app.router.add_post('/debug-clear-service', handlers.debug_clear_service)


def create_application(config, loop=None):
    app = web.Application()

    app['config'] = config

    log.initilize(config['log'])

    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)

    register_routers(app)

    return app


def run_utility(config, utility):

    async def runner():
        await initialize(config)

        log.initilize(config['log'])

        await utility()

        await deinitialize(config)

    asyncio.get_event_loop().run_until_complete(runner())
