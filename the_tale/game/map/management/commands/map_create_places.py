# coding: utf-8
import subprocess

from textgen.words import Noun

from dext.utils import s11n

from django.core.management.base import BaseCommand

from dext.utils.decorators import nested_commit_on_success

from game.balance import constants as c
from game.balance.enums import RACE

from game.game_info import GENDER
from game.prototypes import TimePrototype

from game.map.roads.models import Road
from game.map.places.models import Place
from game.map.places.prototypes import PlacePrototype
from game.map.places.conf import places_settings
from game.map.places.storage import places_storage
from game.map.roads.storage import roads_storage

from game.persons.prototypes import PersonPrototype
from game.persons.storage import persons_storage
from game.persons.conf import persons_settings
from game.persons.relations import PERSON_TYPE


class Command(BaseCommand):

    help = 'create places'

    def handle(self, *args, **options):

        # to sync map size and do other unpredictable operations
        subprocess.call(['./manage.py', 'map_update_map'])

        self.create_place(name=u'Ашур-Донал',
                          x=32,
                          y=6,
                          size=1,
                          roads_to=[places_storage[3],
                                    places_storage[13]],
                          persons=[(u'Лаз',         0.12, RACE.HUMAN,  GENDER.MASCULINE, PERSON_TYPE.MERCHANT),
                                   (u'Antermil',    0.12, RACE.ELF,    GENDER.MASCULINE, PERSON_TYPE.WARDEN),
                                   (u'Snorri',      0.12, RACE.ORC,    GENDER.MASCULINE, PERSON_TYPE.WARDEN),
                                   (u'Dooluni',     0.40, RACE.DWARF,  GENDER.MASCULINE, PERSON_TYPE.BLACKSMITH),
                                   (u'Soo-Ju-Seer', 0.26, RACE.GOBLIN, GENDER.MASCULINE, PERSON_TYPE.ALCHEMIST),
                                   (u'Faerlysi',    0.08, RACE.ELF,    GENDER.FEMININE,  PERSON_TYPE.ALCHEMIST)])

        self.create_place(name=u'Лорадо',
                          x=8,
                          y=24,
                          size=10,
                          roads_to=[places_storage[8]],
                          persons=[(u'San-Joon',    0.27, RACE.GOBLIN,  GENDER.MASCULINE, PERSON_TYPE.CARPENTER),
                                   (u'Laon-Hu',     0.24, RACE.GOBLIN,  GENDER.MASCULINE, PERSON_TYPE.INNKEEPER),
                                   (u'Dafar',       0.24, RACE.ELF,     GENDER.MASCULINE, PERSON_TYPE.BUREAUCRAT),
                                   (u'Venhil',      0.19, RACE.ELF,     GENDER.MASCULINE, PERSON_TYPE.HUNTER),
                                   (u'Размаил',     0.12, RACE.HUMAN,   GENDER.MASCULINE, PERSON_TYPE.WARDEN),
                                   (u'Qasad',       0.06, RACE.ORC,     GENDER.MASCULINE,  PERSON_TYPE.BLACKSMITH)])

        # update map with new places
        subprocess.call(['./manage.py', 'map_update_map'])


    @nested_commit_on_success
    def create_place(self, name, x, y, size, roads_to, persons):

        place_power = int(max(place.power for place in places_storage.all()) * float(size) / places_settings.MAX_SIZE)

        place_power_steps = int(places_settings.POWER_HISTORY_LENGTH / c.MAP_SYNC_TIME)
        place_power_per_step = (place_power / place_power_steps) + 1

        place = PlacePrototype(Place.objects.create( x=x,
                                                     y=y,
                                                     name=name,
                                                     name_forms=s11n.to_json(Noun.fast_construct(name).serialize()),
                                                     size=size))

        initial_turn = TimePrototype.get_current_turn_number() - places_settings.POWER_HISTORY_LENGTH
        for i in xrange(place_power_steps):
            place.push_power(int(initial_turn+i*c.MAP_SYNC_TIME), int(place_power_per_step))

        for name, power_percent, race, gender, tp in persons:
            person = PersonPrototype.create(place=place,
                                            race=race,
                                            gender=gender,
                                            tp=tp,
                                            name=name)
            person_power = place_power * power_percent
            person_power_steps = int(persons_settings.POWER_HISTORY_LENGTH / c.MAP_SYNC_TIME)
            person_power_per_step = (person_power / person_power_steps) + 1
            initial_turn = TimePrototype.get_current_turn_number() - persons_settings.POWER_HISTORY_LENGTH
            for i in xrange(person_power_steps):
                person.push_power(int(initial_turn+i*c.MAP_SYNC_TIME), int(person_power_per_step))
            person.save()

        persons_storage.update_version()

        place.sync_race()
        place.save()

        for destination in roads_to:
            Road.objects.create(point_1=place._model, point_2=destination._model)

        places_storage.update_version()
        roads_storage.update_version()
