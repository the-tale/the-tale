# coding: utf-8

from django.core.management.base import BaseCommand

from ...workers.environment import workers_environment

class Command(BaseCommand):

    help = 'run game supervisor'

    requires_model_validation = False

    def handle(self, *args, **options):

        workers_environment.clean_queues()

        workers_environment.supervisor.initialize()

        workers_environment.supervisor.run()

        workers_environment.deinitialize()
