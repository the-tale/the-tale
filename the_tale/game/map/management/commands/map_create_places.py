# coding: utf-8
from django.core.management.base import BaseCommand
from django.db import transaction

from dext.common.utils.logic import run_django_command

from the_tale.game.balance import constants as c
from the_tale.game.prototypes import TimePrototype

from the_tale.game.map.roads.models import Road
from the_tale.game.map.places.prototypes import PlacePrototype
from the_tale.game.map.places.conf import places_settings
from the_tale.game.map.places.storage import places_storage
from the_tale.game.map.roads.storage import roads_storage
from the_tale.game.map.roads.logic import update_waymarks

from the_tale.game.persons.prototypes import PersonPrototype
from the_tale.game.persons.storage import persons_storage
from the_tale.game.persons import conf as persons_conf
from the_tale.game.persons import logic as persons_logic

from the_tale.linguistics.lexicon.dictionary import noun


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


    def _create_place(self, x, y, roads_to, name_forms):
        return self.create_place(name_forms=name_forms,
                                 x=x,
                                 y=y,
                                 size=1,
                                 is_frontier=True,
                                 roads_to=roads_to)

    def run(self, *args, **kwargs):

        # to sync map size and do other unpredictable operations
        run_django_command(['map_update_map'])

        self.INITIAL_PERSON_POWER = persons_storage.get_medium_power_for_person()

        with transaction.atomic():

            p35 = places_storage[35]
            p35._model.is_frontier = False
            p35.save()

            p8x13 = self._create_place(x=8, y=13, roads_to=[p35],
                               name_forms=noun(forms=(u'Сольвейг', u'Сольвейга', u'Сольвейгу', u'Сольвейг', u'Сольвейгом', u'Сольвейге',
                                                      u'Сольвейги', u'Сольвейгов', u'Сольвейгам', u'Сольвейги', u'Сольвейгами', u'Сольвейгах'),
                                               properties=(u'мр,но')))



            p39 = places_storage[39]
            p39._model.is_frontier = False
            p39.save()

            p52x26 = self._create_place(x=52, y=26, roads_to=[p39, places_storage[40]],
                                       name_forms=noun(forms=(u'Аматир', u'Аматира', u'Аматиру', u'Аматир', u'Аматиром', u'Аматире',
                                                              u'Аматиры', u'Аматиров', u'Аматирам', u'Аматиры', u'Аматирами', u'Аматирах'),
                                                       properties=(u'мр,но')))

            p36 = places_storage[36]
            p36._model.is_frontier = False
            p36.save()

            p22x8 = self._create_place(x=22, y=8, roads_to=[p36],
                                       name_forms=noun(forms=(u'Залесье', u'Залесья', u'Залесью', u'Залесье', u'Залесьем', u'Залесье',
                                                              u'Залесьи', u'Залесьев', u'Залесьям', u'Залесьи', u'Залесьями', u'Залесьях'),
                                                        properties=(u'ср,но')))

        update_waymarks()
        persons_logic.sync_social_connections()


        # update map with new places
        run_django_command(['map_update_map'])


    @transaction.atomic
    def create_place(self, x, y, size, roads_to, persons=(), name_forms=None, is_frontier=False): # pylint: disable=R0914

        place_power = int(max(place.power for place in places_storage.all()) * float(size) / places_settings.MAX_SIZE)

        place_power_steps = int(places_settings.POWER_HISTORY_LENGTH / c.MAP_SYNC_TIME)
        place_power_per_step = (place_power / place_power_steps) + 1

        place = PlacePrototype.create( x=x,
                                       y=y,
                                       utg_name=name_forms.word,
                                       is_frontier=is_frontier,
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
            person_power_steps = int(persons_conf.settings.POWER_HISTORY_LENGTH / c.MAP_SYNC_TIME)
            person_power_per_step = (person_power / person_power_steps) + 1
            initial_turn = TimePrototype.get_current_turn_number() - persons_conf.settings.POWER_HISTORY_LENGTH
            for i in xrange(person_power_steps):
                person.push_power(int(initial_turn+i*c.MAP_SYNC_TIME), int(person_power_per_step))
            person.save()

        place.sync_persons(force_add=True)

        power_delta = self.INITIAL_PERSON_POWER

        for person in place.persons:
            person.fill_power_evenly(power_delta)
            person.save()
            power_delta /= 2

        place.sync_race()
        place.save()

        for destination in roads_to:
            Road.objects.create(point_1=place._model, point_2=destination._model)

        persons_storage.update_version()
        places_storage.update_version()
        roads_storage.update_version()

        persons_storage.refresh()
        places_storage.refresh()
        roads_storage.refresh()

        return place
