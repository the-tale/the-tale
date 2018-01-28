
from aiohttp import web

from tt_web import log
from tt_web import postgresql


async def on_startup(app):
    await postgresql.initialize(app['config']['database'], loop=app.loop)


async def on_cleanup(app):
    await postgresql.deinitialize()


def register_routers(app):
    from . import handlers

    app.router.add_post('/place-sell-lot', handlers.place_sell_lot)
    app.router.add_post('/close-sell-lot', handlers.close_sell_lot)
    app.router.add_post('/cancel-sell-lot', handlers.cancel_sell_lot)
    app.router.add_post('/list-sell-lots', handlers.list_sell_lots)

    app.router.add_post('/info', handlers.info)
    app.router.add_post('/item-type-prices', handlers.item_type_prices)

    app.router.add_post('/statistics', handlers.statistics)

    app.router.add_post('/history', handlers.history)

    app.router.add_post('/debug-clear-service', handlers.debug_clear_service)


def create_application(config, loop=None):
    app = web.Application(loop=loop)

    app['config'] = config

    log.initilize(config['log'])

    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)

    register_routers(app)

    return app
