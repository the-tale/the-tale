# coding: utf-8

from django.core.management.base import BaseCommand

# from game.prototypes import TimePrototype

from game.map.storage import map_info_storage
from game.map.generator import update_map

from optparse import make_option

class Command(BaseCommand):

    help = 'generate map'

    requires_model_validation = False

    option_list = BaseCommand.option_list + ( make_option('-n', '--number',
                                                          action='store',
                                                          type=int,
                                                          dest='repeate_number',
                                                          default=1,
                                                          help='howe many times do generation'), )


    def handle(self, *args, **options):

        for i in xrange(options['repeate_number']):
            print i
            # game_time = TimePrototype.get_current_time()
            update_map(index=map_info_storage.item.id+1)
