# coding: utf-8
import sys
import traceback

from django.core.management.base import BaseCommand
from django.utils.log import getLogger

from dext.utils import pid

from post_service.workers.environment import workers_environment

logger = getLogger('the-tale.workers.post_service_message_sender')

class Command(BaseCommand):

    help = 'run post service message sender worker'

    requires_model_validation = False

    @pid.protector('post_service_message_sender')
    def handle(self, *args, **options):

        try:
            workers_environment.clean_queues()
            workers_environment.message_sender.initialize()
            workers_environment.message_sender.run()
        except KeyboardInterrupt:
            pass
        except Exception:
            traceback.print_exc()
            logger.error('Infrastructure worker exception: post_service_message_sender',
                         exc_info=sys.exc_info(),
                         extra={} )

        workers_environment.deinitialize()
