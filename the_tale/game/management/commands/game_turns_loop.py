# coding: utf-8
import time

from django.core.management.base import BaseCommand

from ...workers.environment import workers_environment
from ... import settings as game_settings

class Command(BaseCommand):

    help = 'run game turns loop'

    requires_model_validation = False

    def handle(self, *args, **options):

        while True:
            time.sleep(game_settings.TURN_DELAY)

            workers_environment.supervisor.cmd_next_turn()
