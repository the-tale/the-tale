
from aiohttp import web

from tt_web import log
from tt_web import postgresql


async def on_startup(app):
    await postgresql.initialize(app['config']['database'])


async def on_cleanup(app):
    await postgresql.deinitialize()


def register_routers(app):
    from . import handlers

    app.router.add_post('/set-properties', handlers.set_properties)
    app.router.add_post('/get-properties', handlers.get_properties)

    app.router.add_post('/data-protection-collect-data', handlers.data_protection_collect_data)
    app.router.add_post('/data-protection-delete-data', handlers.data_protection_delete_data)

    app.router.add_post('/debug-clear-service', handlers.debug_clear_service)


def create_application(config):
    app = web.Application()

    app['config'] = config

    log.initilize(config['log'])

    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)

    register_routers(app)

    return app
