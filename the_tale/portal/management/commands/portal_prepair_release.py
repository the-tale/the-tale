# coding: utf-8
import sys
import subprocess
from optparse import make_option

from django.core.management.base import BaseCommand
from django.conf import settings as project_settings

from dext.utils.meta_config import MetaConfig

meta_config = MetaConfig(config_path=project_settings.META_CONFIG_FILE)

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
        print 'GENEREATE ABILITIES JS'
        print

        subprocess.call(['./manage.py', 'abilities_create_abilities_js'])

        print
        print 'GENERATE JAVASCRIPT CONSTANTS'
        print

        subprocess.call(['./manage.py', 'game_generate_js'])

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
        meta_config.version = version
        meta_config.save_config()
