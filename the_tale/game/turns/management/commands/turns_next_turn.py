# -*- coding: utf-8 -*-
import sys
from django.core.management.base import BaseCommand
from django.db import connection
from django.conf import settings as project_settings
from optparse import make_option

# from ...logic import next_turn
# from ...prototypes import get_latest_turn

# some strange import for command work correctly

from ....map.roads.models import Road # just to awoid django error on startup

from ...logic import next_turn
from ...prototypes import get_latest_turn

class Command(BaseCommand):

    help = 'make next turn'

    # requires_model_validation = False

    option_list = BaseCommand.option_list + (
        make_option('-n', '--number',
                    action='store',
                    type=int,
                    dest='number',
                    default=1,
                    help='specify number of processing turns'),
        )


    def handle(self, *args, **options):

        number = options['number']

        sys.stdout.write('make %i turns\n' % number)
        sys.stdout.flush()

        if project_settings.DEBUG_DB:
            print 'queries before turns: %d' % len(connection.queries)

        while number > 0:

            sys.stdout.write('turns left %i\n' % number)
            sys.stdout.flush()

            number -= 1
            
            cur_turn = get_latest_turn()

            next_turn(cur_turn)

        sys.stdout.write('processed\n')
        sys.stdout.flush()

        if project_settings.DEBUG_DB:
            print 'queries after turns: %d' % len(connection.queries)
