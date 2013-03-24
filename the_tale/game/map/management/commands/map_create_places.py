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

        with nested_commit_on_success():

            self.create_place(name=u'33x11', x=33, y=11, size=1, roads_to=[places_storage[19],
                                                                           places_storage[17]])

            self.create_place(name=u'30x23', x=30, y=23, size=1, roads_to=[places_storage[18]])

            p22x20 = self.create_place(name=u'22x23', x=22, y=23, size=1, roads_to=[places_storage[18],
                                                                                    places_storage[15]])

            self.create_place(name=u'15x21', x=15, y=21, size=1, roads_to=[p22x20,
                                                                           places_storage[15],
                                                                           places_storage[20]])

        # update map with new places
        subprocess.call(['./manage.py', 'map_update_map'])


    @nested_commit_on_success
    def create_place(self, name, x, y, size, roads_to, persons=[]):

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

        place.sync_persons()
        place.sync_race()
        place.save()

        for destination in roads_to:
            Road.objects.create(point_1=place._model, point_2=destination._model)

        places_storage.update_version()
        roads_storage.update_version()

        return place
