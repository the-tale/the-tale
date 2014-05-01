# coding: utf-8
import random

from textgen.words import Noun

from dext.utils import s11n

from django.core.management.base import BaseCommand
from django.db import transaction

from the_tale.common.utils.logic import run_django_command

from the_tale.game.balance import constants as c
from the_tale.game import names
from the_tale.game.relations import GENDER, RACE
from the_tale.game.prototypes import TimePrototype

from the_tale.game.map.roads.models import Road
from the_tale.game.map.places.models import Place
from the_tale.game.map.places.prototypes import PlacePrototype
from the_tale.game.map.places.conf import places_settings
from the_tale.game.map.places.storage import places_storage
from the_tale.game.map.roads.storage import roads_storage

from the_tale.game.persons.prototypes import PersonPrototype
from the_tale.game.persons.storage import persons_storage
from the_tale.game.persons.conf import persons_settings
from the_tale.game.persons.relations import PERSON_TYPE


class Command(BaseCommand):

    help = 'create places'

    def handle(self, *args, **kwargs):
        try:
            self.run()
        except Exception:
            import sys
            import traceback
            traceback.print_exc()
            print sys.exc_info()

            raise

    def run(self, *args, **kwargs):

        # to sync map size and do other unpredictable operations
        run_django_command(['map_update_map'])

        with transaction.atomic():

            self.create_place(name_forms=Noun(normalized=u'Карахен',
                                              forms=(u'Карахен', u'Карахена', u'Карахену', u'Карахен', u'Карахеном', u'Карахене',
                                                     u'Карахены', u'Карахенов', u'Карахенам', u'Карахены', u'Карахенами', u'Карахенах'),
                                              properties=(u'мр')),
                              x=26,
                              y=35,
                              size=1,
                              roads_to=[places_storage[20], places_storage[22]])

            self.create_place(name_forms=Noun(normalized=u'Коркатталь',
                                              forms=(u'Коркатталь', u'Коркатталя', u'Коркатталю', u'Коркатталь', u'Коркатталем', u'Коркаттале',
                                                     u'Коркаттали', u'Коркатталей', u'Коркатталям', u'Коркаттали', u'Коркатталями', u'Коркатталях'),
                                              properties=(u'мр')),
                              x=4,
                              y=18,
                              size=1,
                              roads_to=[places_storage[5]])

            persons = [ (Noun(normalized=u'Бранд',
                              forms=(u'Бранд', u'Бранда', u'Бранду', u'Бранда', u'Брандом', u'Бранде',
                                     u'Бранды', u'Брандов', u'Брандам', u'Брандов', u'Брандами', u'Брандах'),
                              properties=(u'мр')),
                         0.33,
                         RACE.DWARF,
                         GENDER.MASCULINE,
                         PERSON_TYPE.MAGICIAN),
                        (Noun(normalized=u'Доркин',
                              forms=(u'Доркин', u'Доркина', u'Доркину', u'Доркина', u'Доркином', u'Доркине',
                                     u'Доркины', u'Доркинов', u'Доркинам', u'Доркинов', u'Доркинами', u'Доркинах'),
                              properties=(u'мр')),
                         0.33,
                         RACE.DWARF,
                         GENDER.MASCULINE,
                         PERSON_TYPE.BLACKSMITH),
                        (Noun(normalized=u'Горкин',
                              forms=(u'Горкин', u'Горкина', u'Горкину', u'Горкина', u'Горкином', u'Горкине',
                                     u'Горкины', u'Горкинов', u'Горкинам', u'Горкинов', u'Горкинами', u'Горкинах'),
                              properties=(u'мр')),
                         0.33,
                         RACE.DWARF,
                         GENDER.MASCULINE,
                         PERSON_TYPE.MINER) ]

            self.create_place(name_forms=Noun(normalized=u'Карнгард',
                                              forms=(u'Карнгард', u'Карнгарда', u'Карнгарду', u'Карнгард', u'Карнгардом', u'Карнгарде',
                                                     u'Карнгарды', u'Карнгардов', u'Карнгардам', u'Карнгарды', u'Карнгардами', u'Карнгардах'),
                                              properties=(u'мр')),
                              x=31,
                              y=1,
                              size=1,
                              roads_to=[places_storage[24]],
                              persons=persons)

        # update map with new places
        run_django_command(['map_update_map'])


    @transaction.atomic
    def create_place(self, x, y, size, roads_to, persons=(), name_forms=None): # pylint: disable=R0914

        place_power = int(max(place.power for place in places_storage.all()) * float(size) / places_settings.MAX_SIZE)

        place_power_steps = int(places_settings.POWER_HISTORY_LENGTH / c.MAP_SYNC_TIME)
        place_power_per_step = (place_power / place_power_steps) + 1

        place = PlacePrototype.create( x=x,
                                       y=y,
                                       name_forms=name_forms,
                                       size=size)

        initial_turn = TimePrototype.get_current_turn_number() - places_settings.POWER_HISTORY_LENGTH
        for i in xrange(place_power_steps):
            place.push_power(int(initial_turn+i*c.MAP_SYNC_TIME), int(place_power_per_step))

        for person_name_forms, power_percent, race, gender, tp in persons:
            person = PersonPrototype.create(place=place,
                                            race=race,
                                            gender=gender,
                                            tp=tp,
                                            name_forms=person_name_forms)

            person_power = place_power * power_percent
            person_power_steps = int(persons_settings.POWER_HISTORY_LENGTH / c.MAP_SYNC_TIME)
            person_power_per_step = (person_power / person_power_steps) + 1
            initial_turn = TimePrototype.get_current_turn_number() - persons_settings.POWER_HISTORY_LENGTH
            for i in xrange(person_power_steps):
                person.push_power(int(initial_turn+i*c.MAP_SYNC_TIME), int(person_power_per_step))
            person.save()

        persons_storage.update_version()

        place.sync_persons(force_add=True)
        place.sync_race()
        place.save()

        for destination in roads_to:
            Road.objects.create(point_1=place._model, point_2=destination._model)

        places_storage.update_version()
        roads_storage.update_version()

        return place
