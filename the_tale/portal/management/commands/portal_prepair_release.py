# coding: utf-8
import sys
from optparse import make_option

from django.core.management.base import BaseCommand
from django.conf import settings as project_settings

from the_tale.common.utils.logic import run_django_command

META_CONFIG = project_settings.META_CONFIG

class Command(BaseCommand):

    help = 'prepair all generated static files'

    requires_model_validation = False

    option_list = BaseCommand.option_list + ( make_option('-g', '--game-version',
                                                          action='store',
                                                          type=str,
                                                          dest='game-version',
                                                          help='game version'),
                                              )


    def handle(self, *args, **options):

        version = options['game-version']

        if version is None:
            print >> sys.stderr, 'game version MUST be specified'
            sys.exit(1)

        print
        print 'GENERATE JAVASCRIPT CONSTANTS'
        print

        run_django_command(['game_generate_js'])

        print
        print 'GENERATE CSS'
        print

        run_django_command(['less_generate_css'])

        print
        print 'LOAD TEXTGEN TEXTS'
        print

        run_django_command(['game_load_texts'])

        print
        print 'GENERATE META CONFIG'
        print

        META_CONFIG.increment_static_data_version()
        META_CONFIG.version = version
        META_CONFIG.save_config()
