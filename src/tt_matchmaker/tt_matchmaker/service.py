
from aiohttp import web

from tt_web import log
from tt_web import postgresql


async def on_startup(app):
    await postgresql.initialize(app['config']['database'], loop=app.loop)


async def on_cleanup(app):
    await postgresql.deinitialize()


def register_routers(app):
    from . import handlers

    app.router.add_post('/create-battle-request', handlers.create_battle_request)
    app.router.add_post('/cancel-battle-request', handlers.cancel_battle_request)
    app.router.add_post('/accept-battle-request', handlers.accept_battle_request)

    app.router.add_post('/create-battle', handlers.create_battle)

    app.router.add_post('/get-battle-requests', handlers.get_battle_requests)
    app.router.add_post('/get-info', handlers.get_info)

    app.router.add_post('/finish-battle', handlers.finish_battle)

    app.router.add_post('/get-battles-by-participants', handlers.get_battles_by_participants)

    app.router.add_post('/debug-clear-service', handlers.debug_clear_service)


def create_application(config, loop=None):
    app = web.Application(loop=loop)

    app['config'] = config

    log.initilize(config['log'])

    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)

    register_routers(app)

    return app
