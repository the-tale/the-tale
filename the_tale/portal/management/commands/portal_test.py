# coding: utf-8
import pymorphy
from django.core.management.base import BaseCommand

from game.persons.models import Person
from game.persons.prototypes import PersonPrototype

from game.text_generation import get_vocabulary, get_dictionary, prepair_substitution

from textgen.conf import textgen_settings
from textgen.logic import efication, get_gram_info, PROPERTIES

from game.heroes.prototypes import HeroPrototype

morph = pymorphy.get_morph(textgen_settings.PYMORPHY_DICTS_DIRECTORY)

class Command(BaseCommand):

    def handle(self, *args, **options):

        hero = HeroPrototype.get_by_id(1)

        print hero.gender_verbose

        hero.add_message('action_regenerate_energy_start_pray', hero=hero)
