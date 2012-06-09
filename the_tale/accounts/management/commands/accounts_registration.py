# coding: utf-8
import sys
import traceback

from django.core.management.base import BaseCommand
from django.utils.log import getLogger

from dext.utils import pid

from portal.workers.environment import workers_environment


logger = getLogger('accounts.workers.registration')

class Command(BaseCommand):

    help = 'run accounts registration'

    requires_model_validation = False

    @pid.protector('accounts_registration')
    def handle(self, *args, **options):

        try:
            workers_environment.clean_queues()
            workers_environment.registration.initialize()
            workers_environment.registration.run()
        except KeyboardInterrupt:
            pass
        except Exception:
            traceback.print_exc()
            logger.error('Infrastructure worker exception: accounts_registration',
                         exc_info=sys.exc_info(),
                         extra={} )


        workers_environment.deinitialize()
