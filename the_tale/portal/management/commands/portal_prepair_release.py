# coding: utf-8
import sys
import subprocess
from optparse import make_option

from django.core.management.base import BaseCommand

from meta_config import meta_config

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

        game_version = options['game-version']

        if game_version is None:
            print >> sys.stderr, 'game version MUST be specified'
            sys.exit(1)

        print
        print 'GENEREATE ABILITIES JS'
        print

        subprocess.call(['./manage.py', 'abilities_create_abilities_js'])

        print
        print 'GENERATE CSS'
        print

        subprocess.call(['./manage.py', 'less_generate_css'])

        print
        print 'LOAD TEXTGEN TEXTS'
        print

        subprocess.call(['./manage.py', 'game_load_texts'])

        print
        print 'GENERATE META CONFIG'
        print

        meta_config.increment_static_data_version()
        meta_config.game_version = game_version
        meta_config.save_config()
