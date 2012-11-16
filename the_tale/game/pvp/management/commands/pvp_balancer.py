# coding: utf-8
import sys
import traceback

from django.core.management.base import BaseCommand
from django.utils.log import getLogger

from dext.utils import pid

from game.workers.environment import workers_environment

logger = getLogger('the-tale.workers.game_pvp_balancer')

class Command(BaseCommand):

    help = 'run game pvp balancer'

    requires_model_validation = False

    @pid.protector('game_pvp_balancer')
    def handle(self, *args, **options):

        try:
            workers_environment.pvp_balancer.run()
        except KeyboardInterrupt:
            pass
        except Exception:
            traceback.print_exc()
            logger.error('Game worker exception: pvp balancer',
                         exc_info=sys.exc_info(),
                         extra={} )

        workers_environment.deinitialize()
