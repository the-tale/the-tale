
from aiohttp import web

from tt_web import log
from tt_web import postgresql

from . import operations


async def on_startup(app):
    await postgresql.initialize(app['config']['database'], loop=app.loop)


async def on_cleanup(app):
    await postgresql.deinitialize()


def register_routers(app):
    from . import handlers

    app.router.add_post('/apply', handlers.apply)
    app.router.add_post('/get-items', handlers.get_items)
    app.router.add_post('/has-items', handlers.has_items)

    app.router.add_post('/debug-clear-service', handlers.debug_clear_service)


def create_application(config, loop=None):
    app = web.Application(loop=loop)

    app['config'] = config

    log.initilize(config['log'])

    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)

    register_routers(app)

    return app
