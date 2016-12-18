
import logging

from aiohttp import web

from . import utils
from . import postgresql
from . import operations


LOG_FORMAT = '[%(levelname)s %(asctime)s %(module)s %(process)d] %(message)s'


def initilize_log(config):
    root = logging.getLogger()

    root.setLevel(getattr(logging, config['level'].upper()))

    logging.basicConfig(format=LOG_FORMAT)


async def on_startup(app):
    await postgresql.initialize(app['config']['database'], loop=app.loop)

    await operations.initialize_timestamps_cache()


async def on_cleanup(app):
    await postgresql.deinitialize()


def register_routers(app):
    from . import handlers

    app.router.add_post('/version', handlers.version)
    app.router.add_post('/push-message', handlers.push_message)
    app.router.add_post('/diary', handlers.diary)


def create_application(config, loop=None):
    app = web.Application(loop=loop)

    app['config'] = config

    initilize_log(config['log'])

    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)

    register_routers(app)

    return app
