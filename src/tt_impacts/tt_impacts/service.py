
from aiohttp import web

from tt_web import log
from tt_web import postgresql


async def on_startup(app):
    await postgresql.initialize(app['config']['database'], loop=app.loop)


async def on_cleanup(app):
    await postgresql.deinitialize()


def register_routers(app):
    from . import handlers

    app.router.add_post('/add-impacts', handlers.add_impacts)
    app.router.add_post('/get-impacts-history', handlers.get_impacts_history)
    app.router.add_post('/get-targets-impacts', handlers.get_targets_impacts)
    app.router.add_post('/get-actor-impacts', handlers.get_actor_impacts)
    app.router.add_post('/get-impacters-ratings', handlers.get_impacters_ratings)
    app.router.add_post('/scale-impacts', handlers.scale_impacts)

    app.router.add_post('/debug-clear-service', handlers.debug_clear_service)


def create_application(config, loop=None):
    app = web.Application(loop=loop)

    app['config'] = config

    log.initilize(config['log'])

    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)

    register_routers(app)

    return app
