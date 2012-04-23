# coding: utf-8
import pymorphy

from django.core.management.base import BaseCommand

from ...storage import MobsDatabase

from ....textgen.templates import Dictionary
from ....textgen.words import WordBase
from ....textgen.logic import get_tech_vocabulary
from ....textgen.conf import textgen_settings

morph = pymorphy.get_morph(textgen_settings.PYMORPHY_DICTS_DIRECTORY)


class Command(BaseCommand):

    help = 'load mobs texts into database'

    def handle(self, *args, **options):

        dictionary = Dictionary()
        dictionary.load()
        tech_vocabulary = get_tech_vocabulary()

        for mob_record in MobsDatabase.storage().data.values():
            word = WordBase.create_from_string(morph, mob_record.normalized_name, tech_vocabulary)
            dictionary.add_word(word)

        dictionary.save()
