# coding: utf-8

from django.core.management.base import BaseCommand

from dext.utils import pid

from ...workers.environment import workers_environment

class Command(BaseCommand):

    help = 'run game supervisor'

    requires_model_validation = False

    def handle(self, *args, **options):

        with pid.wrap('game_supervisor'):
            try:
                workers_environment.clean_queues()
                workers_environment.supervisor.initialize()
                workers_environment.supervisor.run()
            except KeyboardInterrupt:
                pass

            workers_environment.deinitialize()
