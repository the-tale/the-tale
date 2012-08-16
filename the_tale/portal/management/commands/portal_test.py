# coding: utf-8
import pymorphy
from django.core.management.base import BaseCommand

from game.persons.models import Person
from game.persons.prototypes import PersonPrototype

from game.text_generation import get_vocabulary, get_dictionary, prepair_substitution

from textgen.conf import textgen_settings
from textgen.logic import efication, get_gram_info, PROPERTIES

morph = pymorphy.get_morph(textgen_settings.PYMORPHY_DICTS_DIRECTORY)

class Command(BaseCommand):

    def handle(self, *args, **options):

        runa = PersonPrototype(Person.objects.get(name='Runa'))

        print runa.normalized_name[1]

        # print get_vocabulary().data.keys()

        template = get_vocabulary().get_random_phrase('quest_notmywork_diary_choice_do_work', None)
        substitution = prepair_substitution({'person_end': runa})

        # template = get_vocabulary().get_random_phrase('angel_ability_healhero', None)
        # substitution = {"hero": (u"привидение", u"жр"), "health": 13}

        result = template.substitute(get_dictionary(), substitution)

        print result
