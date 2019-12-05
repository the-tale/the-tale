
from aiohttp import web

from tt_web import log
from tt_web import postgresql

from . import operations


async def on_startup(app):
    await postgresql.initialize(app['config']['database'])

    await operations.initialize_timestamps_cache()


async def on_cleanup(app):
    await postgresql.deinitialize()


def register_routers(app):
    from . import handlers

    app.router.add_post('/version', handlers.version)
    app.router.add_post('/push-message', handlers.push_message)
    app.router.add_post('/diary', handlers.diary)


def create_application(config):
    app = web.Application()

    app['config'] = config

    log.initilize(config['log'])

    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)

    register_routers(app)

    return app
