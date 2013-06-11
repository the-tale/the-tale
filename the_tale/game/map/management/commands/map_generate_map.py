# coding: utf-8
import sys
import traceback

from django.core.management.base import BaseCommand
from django.utils.log import getLogger

from game.map.storage import map_info_storage
from game.map.generator import update_map

from optparse import make_option

logger = getLogger('the-tale.workers.game_highlevel')

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

        try:
            for i in xrange(options['repeate_number']): # pylint: disable=W0612
                # print i
                update_map(index=map_info_storage.item.id+1)
        except Exception: # pylint: disable=W0703
            traceback.print_exc()
            logger.error('Map generation exception',
                         exc_info=sys.exc_info(),
                         extra={} )
