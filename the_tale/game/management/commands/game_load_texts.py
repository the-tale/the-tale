# coding: utf-8
import pymorphy

from django.core.management.base import BaseCommand

from game.mobs import logic as mobs_logic
from game.artifacts import logic as artifacts_logic

from game.textgen.conf import textgen_settings
from game.textgen import logic as textgen_logic

morph = pymorphy.get_morph(textgen_settings.PYMORPHY_DICTS_DIRECTORY)


class Command(BaseCommand):

    help = 'load all texts into database'

    def handle(self, *args, **options):

        print "LOAD MOB'S NAMES"
        mobs_logic.import_texts_into_database(morph)

        print "LOAD ARTIFACT'S NAMES"
        artifacts_logic.import_texts_into_database(morph)

        print "LOAD MESSAGES"
        textgen_logic.import_texts_into_database(morph)
