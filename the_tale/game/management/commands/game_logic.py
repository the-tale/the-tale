# coding: utf-8

from django.core.management.base import BaseCommand

from dext.utils import pid

from ...workers.environment import workers_environment

class Command(BaseCommand):

    help = 'run game logic'

    requires_model_validation = False

    def handle(self, *args, **options):

        with pid.wrap('game_logic'):
            try:
                workers_environment.logic.run()
            except KeyboardInterrupt:
                pass

            workers_environment.deinitialize()
