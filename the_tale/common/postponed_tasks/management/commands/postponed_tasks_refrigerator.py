# coding: utf-8
import sys
import traceback

from django.core.management.base import BaseCommand
from django.utils.log import getLogger

from dext.utils import pid

from common.postponed_tasks.workers.environment import workers_environment as postponed_tasks_workers_environment

logger = getLogger('the-tale.workers.postponed_tasks_refrigerator')

class Command(BaseCommand):

    help = 'run postponed tasks refrigerator worker'

    requires_model_validation = False

    @pid.protector('postponed_tasks_refrigerator')
    def handle(self, *args, **options):

        try:
            postponed_tasks_workers_environment.clean_queues()
            postponed_tasks_workers_environment.refrigerator.initialize()
            postponed_tasks_workers_environment.refrigerator.run()
        except KeyboardInterrupt:
            pass
        except Exception:
            traceback.print_exc()
            logger.error('Infrastructure worker exception: postponed_tasks_refrigerator',
                         exc_info=sys.exc_info(),
                         extra={} )

        postponed_tasks_workers_environment.deinitialize()
