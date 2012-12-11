# coding: utf-8

from django.core.management.base import BaseCommand

from game.prototypes import TimePrototype

from game.map.generator import update_map

class Command(BaseCommand):

    help = 'generate map'

    requires_model_validation = False

    def handle(self, *args, **options):
        game_time = TimePrototype.get_current_time()

        # for i in xrange(100):
            # print i
        # game_time.increment_turn()
        update_map(index=game_time.turn_number)
        # game_time.save()
