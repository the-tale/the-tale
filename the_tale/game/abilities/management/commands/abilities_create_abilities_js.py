# -*- coding: utf-8 -*-
from optparse import make_option

from django.core.management.base import BaseCommand

from django_next.jinja2 import render

from ... import settings as abilities_settings
from ...deck import ABILITIES


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
                                   {'abilities': ABILITIES } )

        with open(OUTPUT_FILE, 'w') as output:
            output.write(abilities_content.encode('utf-8'))

