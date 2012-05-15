# coding: utf-8

from django.core.management.base import BaseCommand

from dext.utils import pid

from ...workers.environment import workers_environment

class Command(BaseCommand):

    help = 'run game supervisor'

    requires_model_validation = False

    def handle(self, *args, **options):

        if not pid.capture('game_supervisor'):
            print 'process has been already running'
            return

        workers_environment.clean_queues()

        workers_environment.supervisor.initialize()

        workers_environment.supervisor.run()

        workers_environment.deinitialize()
