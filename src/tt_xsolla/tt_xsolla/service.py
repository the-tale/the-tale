
import logging
import asyncio

from aiohttp import web

from tt_web import log
from tt_web import postgresql
from tt_web.common import event

from . import conf
from . import logic


PAYMENT_PROCESSING_TASK = None


async def start_payment_processing(config):
    global PAYMENT_PROCESSING_TASK

    async def process_payments():
        event.get(conf.PROCESS_INVOICE_EVENT_NAME).set()

        while True:
            await logic.process_invoices(logic.make_payment, config)
            await asyncio.sleep(config['custom']['sleep_if_no_payments_interval'])

    logging.info('start payment processing background task')

    PAYMENT_PROCESSING_TASK = asyncio.ensure_future(process_payments())


async def stop_payment_processing():
    global PAYMENT_PROCESSING_TASK

    if PAYMENT_PROCESSING_TASK:
        PAYMENT_PROCESSING_TASK.cancel()

    PAYMENT_PROCESSING_TASK = None


async def initialize(config, allow_callbacks):
    await postgresql.initialize(config['database'])

    if allow_callbacks and config['custom']['run_callbacks']:
        await start_payment_processing(config)


async def deinitialize(config):
    await stop_payment_processing()
    await postgresql.deinitialize()


async def on_startup(app):
    await initialize(app['config'], allow_callbacks=True)


async def on_cleanup(app):
    await deinitialize(app['config'])


def register_routers(app):
    from . import handlers

    app.router.add_post('/xsolla-hook', handlers.xsolla_hook)

    app.router.add_post('/get-token', handlers.get_token)

    app.router.add_post('/data-protection-collect-data', handlers.data_protection_collect_data)
    app.router.add_post('/data-protection-delete-data', handlers.data_protection_delete_data)

    app.router.add_post('/debug-clear-service', handlers.debug_clear_service)


def create_application(config, loop=None):
    app = web.Application()

    app['config'] = config

    log.initilize(config['log'])

    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)

    register_routers(app)

    return app


def run_utility(config, utility):

    async def runner():
        await initialize(config, allow_callbacks=False)

        log.initilize(config['log'])

        await utility()

        await deinitialize(config)

    asyncio.get_event_loop().run_until_complete(runner())
