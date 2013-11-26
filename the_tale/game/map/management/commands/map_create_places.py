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

            self.create_place(name=u'Гориндор',
                              name_forms=Noun(normalized=u'Гориндор',
                                              forms=(u'Гориндор', u'Гориндора', u'Гориндору', u'Гориндор', u'Гориндором', u'Гориндоре',
                                                     u'Гориндоры', u'Гориндоров', u'Гориндорам', u'Гориндоры', u'Гориндорами', u'Гориндорах'),
                                              properties=(u'мр')),
                          x=17,
                          y=7,
                          size=10,
                          roads_to=[places_storage[1],
                                    places_storage[2]],
                          persons=[(u'Эбхард Чернобрадый',    0.25, RACE.DWARF, GENDER.MASCULINE, PERSON_TYPE.BLACKSMITH),
                                   (u'Ингварр Одноглазый',    0.25, RACE.DWARF, GENDER.MASCULINE, PERSON_TYPE.BUREAUCRAT),
                                   (u'Дойлин',                0.25, RACE.DWARF, GENDER.MASCULINE, PERSON_TYPE.MAGICIAN),
                                   (u'Уллрэкс Чёрная Секира', 0.25, RACE.DWARF, GENDER.MASCULINE, PERSON_TYPE.WARDEN) ])

            self.create_place(name=u'Лотир-Нериэн',
                              name_forms=Noun(normalized=u'Лотир-Нериэн',
                                              forms=(u'Лотир-Нериэн', u'Лотир-Нериэна', u'Лотир-Нериэну', u'Лотир-Нериэн', u'Лотир-Нериэном', u'Лотир-Нериэне',
                                                     u'Лотир-Нериэны', u'Лотир-Нериэнов', u'Лотир-Нериэнам', u'Лотир-Нериэны', u'Лотир-Нериэнами', u'Лотир-Нериэнах'),
                                              properties=(u'мр')),
                          x=33,
                          y=32,
                          size=3,
                          roads_to=[places_storage[18]],
                          persons=[(u'Andermil',   0.25, RACE.ELF, GENDER.MASCULINE, PERSON_TYPE.EXECUTIONER),
                                   (u'Ku-ling-on', 0.25, RACE.GOBLIN, GENDER.MASCULINE, PERSON_TYPE.MAYOR),
                                   (u'Sinedkorj',  0.25, RACE.ORC, GENDER.MASCULINE, PERSON_TYPE.WARDEN),
                                   (u'Кайлонг',    0.25, RACE.GOBLIN, GENDER.MASCULINE, PERSON_TYPE.ALCHEMIST) ])

            self.create_place(name=u'Лазурь',
                              name_forms=Noun(normalized=u'Лазурь',
                                              forms=(u'Лазурь', u'Лазури', u'Лазури', u'Лазурь', u'Лазурью', u'Лазури',
                                                     u'Лазури', u'Лазури', u'Лазури', u'Лазури', u'Лазурями', u'Лазурях'),
                                              properties=(u'жр')),
                          x=48,
                          y=20,
                          size=3,
                          roads_to=[places_storage[19]],
                          persons=[(None, 0.2, RACE.DWARF, GENDER.MASCULINE, random.choice(PERSON_TYPE.records)),
                                   (None, 0.2, RACE.GOBLIN,GENDER.MASCULINE, random.choice(PERSON_TYPE.records)),
                                   (None, 0.2, RACE.ORC,   GENDER.MASCULINE, random.choice(PERSON_TYPE.records)),
                                   (None, 0.2, RACE.ELF,   GENDER.MASCULINE, random.choice(PERSON_TYPE.records)),
                                   (None, 0.2, RACE.HUMAN, GENDER.MASCULINE, random.choice(PERSON_TYPE.records)) ])



        # update map with new places
        run_django_command(['map_update_map'])


    @transaction.atomic
    def create_place(self, name, x, y, size, roads_to, persons=(), name_forms=None): # pylint: disable=R0914

        place_power = int(max(place.power for place in places_storage.all()) * float(size) / places_settings.MAX_SIZE)

        place_power_steps = int(places_settings.POWER_HISTORY_LENGTH / c.MAP_SYNC_TIME)
        place_power_per_step = (place_power / place_power_steps) + 1

        place = PlacePrototype(Place.objects.create( x=x,
                                                     y=y,
                                                     name=name,
                                                     name_forms=s11n.to_json((Noun.fast_construct(name) if name_forms is None else name_forms).serialize()),
                                                     size=size))

        initial_turn = TimePrototype.get_current_turn_number() - places_settings.POWER_HISTORY_LENGTH
        for i in xrange(place_power_steps):
            place.push_power(int(initial_turn+i*c.MAP_SYNC_TIME), int(place_power_per_step))

        for name, power_percent, race, gender, tp in persons:
            if name is None:
                name = names.generator.get_name(race, gender)

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
