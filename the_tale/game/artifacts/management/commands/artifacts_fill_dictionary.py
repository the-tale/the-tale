# coding: utf-8
import pymorphy

from django.core.management.base import BaseCommand

from game.artifacts.logic import import_texts_into_database

from game.textgen.conf import textgen_settings

morph = pymorphy.get_morph(textgen_settings.PYMORPHY_DICTS_DIRECTORY)

class Command(BaseCommand):

    help = 'load artifacts texts into database'

    def handle(self, *args, **options):
        import_texts_into_database(morph)
