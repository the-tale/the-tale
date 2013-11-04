# coding: utf-8
from optparse import make_option

from django.core.management.base import BaseCommand

from dext.jinja2 import render

from the_tale.game.abilities.conf import abilities_settings
from the_tale.game.abilities.relations import ABILITY_TYPE


class Command(BaseCommand):

    help = 'create javascript file with all abilities data'

    option_list = BaseCommand.option_list + ( make_option('--output-file',
                                                          action='store',
                                                          type=str,
                                                          default=abilities_settings.JS_FILE_LOCATION,
                                                          dest='output_file',
                                                          help='path to generated file'),
                                              )


    def handle(self, *args, **options):

        OUTPUT_FILE = options['output_file']

        abilities_content = render('abilities/management/abilities.js',
                                   {'ABILITY_TYPE': ABILITY_TYPE } )

        with open(OUTPUT_FILE, 'w') as output:
            output.write(abilities_content.encode('utf-8'))
