# coding: utf-8
import sys
import traceback

from django.core.management.base import BaseCommand
from django.utils.log import getLogger

from dext.utils import pid

from bank.workers.environment import workers_environment

logger = getLogger('the-tale.workers.bank_bank_processor')

class Command(BaseCommand):

    help = 'run bank processor service'

    requires_model_validation = False

    @pid.protector('bank_bank_processor')
    def handle(self, *args, **options):

        try:
            workers_environment.clean_queues()
            workers_environment.bank_processor.initialize()
            workers_environment.bank_processor.run()
        except KeyboardInterrupt:
            pass
        except Exception:
            traceback.print_exc()
            logger.error('Infrastructure worker exception: bank_bank_processor',
                         exc_info=sys.exc_info(),
                         extra={} )

        workers_environment.deinitialize()
