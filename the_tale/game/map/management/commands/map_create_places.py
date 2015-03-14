# coding: utf-8
import random

from dext.common.utils import s11n

from django.core.management.base import BaseCommand
from django.db import transaction

from dext.common.utils.logic import run_django_command

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
from the_tale.game.persons import conf import persons_conf
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


    def _create_place(self, x, y, roads_to, name_forms=None):

        if name_forms is None:
            name_forms=Noun.fast_construct(u'%dx%d' % (x, y))

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

            p27x47 = self._create_place(x=27, y=47, roads_to=[places_storage[25]],
                               name_forms=Noun(normalized=u'Эльстер',
                                               forms=(u'Эльстер', u'Эльстера', u'Эльстеру', u'Эльстер', u'Эльстером', u'Эльстере',
                                                      u'Эльстеры', u'Эльстеров', u'Эльстерам', u'Эльстеры', u'Эльстерами', u'Эльстерах'),
                                                      properties=(u'мр')))
            self._create_place(x=19, y=45, roads_to=[p27x47],
                               name_forms=Noun(normalized=u'Ол',
                                               forms=(u'Ол', u'Ола', u'Олу', u'Ол', u'Олом', u'Оле',
                                                      u'Олы', u'Олов', u'Олам', u'Олы', u'Олами', u'Олах'),
                                                      properties=(u'мр')))
            self._create_place(x=40, y=47, roads_to=[places_storage[25]],
                               name_forms=Noun(normalized=u'Ад-Альхар',
                                               forms=(u'Ад-Альхар', u'Ад-Альхара', u'Ад-Альхару', u'Ад-Альхар', u'Ад-Альхаром', u'Ад-Альхаре',
                                                      u'Ад-Альхары', u'Ад-Альхаров', u'Ад-Альхарам', u'Ад-Альхары', u'Ад-Альхарами', u'Ад-Альхарах'),
                                                      properties=(u'мр')))

            p16x34 = self._create_place(x=16, y=34, roads_to=[places_storage[20], places_storage[7]],
                               name_forms=Noun(normalized=u'Мурмеллашум',
                                               forms=(u'Мурмеллашум', u'Мурмеллашума', u'Мурмеллашуму', u'Мурмеллашум', u'Мурмеллашумом', u'Мурмеллашуме',
                                                      u'Мурмеллашумы', u'Мурмеллашумов', u'Мурмеллашумам', u'Мурмеллашумы', u'Мурмеллашумами', u'Мурмеллашумах'),
                                                      properties=(u'мр')))
            self._create_place(x=14, y=28, roads_to=[p16x34, places_storage[26]],
                               name_forms=Noun(normalized=u'Кайлердор',
                                               forms=(u'Кайлердор', u'Кайлердора', u'Кайлердору', u'Кайлердор', u'Кайлердором', u'Кайлердоре',
                                                      u'Кайлердоры', u'Кайлердоров', u'Кайлердорам', u'Кайлердоры', u'Кайлердорами', u'Кайлердорах'),
                                                      properties=(u'мр')))
            self._create_place(x=4, y=26, roads_to=[places_storage[26]],
                               name_forms=Noun(normalized=u'Крепость',
                                               forms=(u'Крепость', u'Крепости', u'Крепости', u'Крепость', u'Крепостью', u'Крепости',
                                                      u'Крепости', u'Крепостей', u'Крепостям', u'Крепости', u'Крепостями', u'Крепостях'),
                                                      properties=(u'мр')))

            self._create_place(x=12, y=17, roads_to=[places_storage[26], places_storage[1]],
                               name_forms=Noun(normalized=u'Пёстрая корова',
                                               forms=(u'Пёстрая корова', u'Пёстрой коровы', u'Пёстрой корове', u'Пёструю корову', u'Пёстрой коровой', u'Пёстрой корове',
                                                      u'Пёстрые коровы', u'Пёстрых коров', u'Пёстрым коровам', u'Пёстрых коров', u'Пёстрыми коровами', u'Пёстрых коровах'),
                                                      properties=(u'мр')))

            p15x6 = self._create_place(x=15, y=6, roads_to=[],
                               name_forms=Noun(normalized=u'Истарост',
                                               forms=(u'Истарост', u'Истароста', u'Истаросту', u'Истарост', u'Истаростом', u'Истаросте',
                                                      u'Истаросты', u'Истаростов', u'Истаростам', u'Истаросты', u'Истаростами', u'Истаростах'),
                                                      properties=(u'мр')))
            p25x3 = self._create_place(x=25, y=3, roads_to=[p15x6, places_storage[24]],
                               name_forms=Noun(normalized=u'Торбал-Морра',
                                               forms=(u'Торбал-Морра', u'Торбал-Морра', u'Торбал-Морра', u'Торбал-Морра', u'Торбал-Морра', u'Торбал-Морра',
                                                      u'Торбал-Морры', u'Торбал-Морров', u'Торбал-Моррам', u'Торбал-Морры', u'Торбал-Моррами', u'Торбал-Моррах'),
                                                      properties=(u'мр')))
            self._create_place(x=37, y=1, roads_to=[p25x3, places_storage[24], places_storage[27]],
                               name_forms=Noun(normalized=u'Азарок',
                                               forms=(u'Азарок', u'Азарока', u'Азароку', u'Азарок', u'Азароком', u'Азароке',
                                                      u'Азароки', u'Азароков', u'Азарокам', u'Азароков', u'Азароками', u'Азароках'),
                                                      properties=(u'мр')))

            p48x7 = self._create_place(x=48, y=7, roads_to=[places_storage[27]],
                               name_forms=Noun(normalized=u'Кель-Аба',
                                               forms=(u'Кель-Аба', u'Кель-Аба', u'Кель-Аба', u'Кель-Аба', u'Кель-Аба', u'Кель-Аба',
                                                      u'Кель-Абы', u'Кель-Аб', u'Кель-Абам', u'Кель-Абы', u'Кель-Абами', u'Кель-Абах'),
                                                      properties=(u'мр')))
            self._create_place(x=46, y=14, roads_to=[p48x7, places_storage[3]],
                               name_forms=Noun(normalized=u'Сва-Лок',
                                               forms=(u'Сва-Лок', u'Сва-Лока', u'Сва-Локу', u'Сва-Лок', u'Сва-Локом', u'Сва-Локе',
                                                      u'Сва-Локи', u'Сва-Локов', u'Сва-Локам', u'Сва-Локов', u'Сва-Локами', u'Сва-Локах'),
                                                      properties=(u'мр')))

            p59x21 = self._create_place(x=59, y=21, roads_to=[places_storage[23]],
                               name_forms=Noun(normalized=u'Синам-Сиджас',
                                               forms=(u'Синам-Сиджас', u'Синам-Сиджаса', u'Синам-Сиджасу', u'Синам-Сиджас', u'Синам-Сиджасом', u'Синам-Сиджасе',
                                                      u'Синам-Сиджасы', u'Синам-Сиджасов', u'Синам-Сиджасам', u'Синам-Сиджасов', u'Синам-Сиджасами', u'Синам-Сиджасах'),
                                                      properties=(u'мр')))
            p62x29 = self._create_place(x=62, y=29, roads_to=[p59x21],
                               name_forms=Noun(normalized=u'Сухой Дол',
                                               forms=(u'Сухой Дол', u'Сухого Дола', u'Сухому Долу', u'Сухой Дол', u'Сухим Долом', u'Сухом Доле',
                                                      u'Сухие Долы', u'Сухих Долов', u'Сухим Долом', u'Сухие Долы', u'Сухими Долами', u'Сухих Долах'),
                                                      properties=(u'мр')))
            p54x32 = self._create_place(x=54, y=32, roads_to=[p62x29, places_storage[23]],
                               name_forms=Noun(normalized=u'Харир',
                                               forms=(u'Харир', u'Харира', u'Хариру', u'Харир', u'Хариром', u'Харире',
                                                      u'Хариры', u'Хариров', u'Харирам', u'Хариров', u'Харирами', u'Харирах'),
                                                      properties=(u'мр')))
            self._create_place(x=59, y=37, roads_to=[p54x32, places_storage[22]],
                               name_forms=Noun(normalized=u'Эйндалион',
                                               forms=(u'Эйндалион', u'Эйндалиона', u'Эйндалиону', u'Эйндалион', u'Эйндалионом', u'Эйндалионе',
                                                      u'Эйндалионы', u'Эйндалионов', u'Эйндалионам', u'Эйндалионы', u'Эйндалионами', u'Эйндалионах'),
                                                      properties=(u'мр')))



        # update map with new places
        run_django_command(['map_update_map'])


    @transaction.atomic
    def create_place(self, x, y, size, roads_to, persons=(), name_forms=None, is_frontier=False): # pylint: disable=R0914

        place_power = int(max(place.power for place in places_storage.all()) * float(size) / places_settings.MAX_SIZE)

        place_power_steps = int(places_settings.POWER_HISTORY_LENGTH / c.MAP_SYNC_TIME)
        place_power_per_step = (place_power / place_power_steps) + 1

        place = PlacePrototype.create( x=x,
                                       y=y,
                                       name_forms=name_forms,
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

        return place
