
import smart_imports

smart_imports.all()


settings = utils_app_settings.app_settings('POSTPONED_TASKS',
                                           TASK_WAIT_DELAY=0.25,
                                           TASK_LIVE_TIME=1 * 24 * 60 * 60)
