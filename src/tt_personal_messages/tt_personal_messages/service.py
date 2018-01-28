
from aiohttp import web

from tt_web import log
from tt_web import postgresql


async def on_startup(app):
    await postgresql.initialize(app['config']['database'], loop=app.loop)


async def on_cleanup(app):
    await postgresql.deinitialize()


def register_routers(app):
    from . import handlers

    app.router.add_post('/new-messages-number', handlers.new_messages_number)
    app.router.add_post('/read-messages', handlers.read_messages)
    app.router.add_post('/send-message', handlers.send_message)
    app.router.add_post('/hide-message', handlers.hide_message)
    app.router.add_post('/hide-all-messages', handlers.hide_all_messages)
    app.router.add_post('/hide-conversation', handlers.hide_conversation)
    app.router.add_post('/remove-old-messages', handlers.remove_old_messages)
    app.router.add_post('/get-messages', handlers.get_messages)
    app.router.add_post('/get-conversation', handlers.get_conversation)
    app.router.add_post('/get-message', handlers.get_message)
    app.router.add_post('/get-contacts', handlers.get_contacts)

    app.router.add_post('/debug-clear-service', handlers.debug_clear_service)


def create_application(config, loop=None):
    app = web.Application(loop=loop)

    app['config'] = config

    log.initilize(config['log'])

    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)

    register_routers(app)

    return app
