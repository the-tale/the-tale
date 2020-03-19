
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

    app.router.add_post('/get-id', handlers.get_id)

    app.router.add_post('/debug-clear-service', handlers.debug_clear_service)


def create_application(config):
    app = web.Application()

    app['config'] = config

    log.initilize(config['log'])

    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)

    register_routers(app)

    return app
