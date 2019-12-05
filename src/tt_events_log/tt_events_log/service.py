
from aiohttp import web

from tt_web import log
from tt_web import postgresql


async def on_startup(app):
    await postgresql.initialize(app['config']['database'])


async def on_cleanup(app):
    await postgresql.deinitialize()


def register_routers(app):
    from . import handlers

    app.router.add_post('/add-event', handlers.add_event)
    app.router.add_post('/get-events', handlers.get_events)
    app.router.add_post('/get-last-events', handlers.get_last_events)

    app.router.add_post('/debug-clear-service', handlers.debug_clear_service)


def create_application(config, loop=None):
    app = web.Application()

    app['config'] = config

    log.initilize(config['log'])

    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)

    register_routers(app)

    return app
