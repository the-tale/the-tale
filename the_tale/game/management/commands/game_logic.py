# coding: utf-8

from django.core.management.base import BaseCommand

from ...workers.environment import workers_environment

class Command(BaseCommand):

    help = 'run game logic'

    requires_model_validation = False

    def handle(self, *args, **options):

        workers_environment.game.run()

        workers_environment.deinitialize()

