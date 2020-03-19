
import asyncio

from aiohttp import web

from tt_web import log
from tt_web import postgresql

from . import operations


FINISH_TIMERS_TASK = None


async def on_startup(app):
    global FINISH_TIMERS_TASK

    await postgresql.initialize(app['config']['database'])

    if not app['start_timers_loop']:
        return

    await operations.load_all_timers()

    def scheduler(finish_timer, timer_id, config):
        app.loop.create_task(finish_timer(timer_id, config))

    async def finish_timers():
        while True:
            operations.finish_completed_timers(scheduler, app['config']['custom'])
            await asyncio.sleep(app['config']['custom']['sleep_if_no_timers_interval'])

    FINISH_TIMERS_TASK = asyncio.ensure_future(finish_timers())


async def on_cleanup(app):
    if FINISH_TIMERS_TASK:
        FINISH_TIMERS_TASK.cancel()

    await postgresql.deinitialize()


def register_routers(app):
    from . import handlers

    app.router.add_post('/create-timer', handlers.create_timer)
    app.router.add_post('/get-owner-timers', handlers.get_owner_timers)
    app.router.add_post('/change-speed', handlers.change_speed)

    app.router.add_post('/debug-clear-service', handlers.debug_clear_service)


def create_application(config, start_timers_loop=True):
    app = web.Application()

    app['config'] = config
    app['start_timers_loop'] = start_timers_loop

    log.initilize(config['log'])

    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)

    register_routers(app)

    return app
