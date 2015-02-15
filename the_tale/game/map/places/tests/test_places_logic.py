# coding: utf-8

import mock

from the_tale.common.utils import testcase

from the_tale.linguistics import logic as linguistics_logic

from the_tale.game import names

from the_tale.game.balance import constants as c
from the_tale.game.relations import RACE
from the_tale.game.prototypes import TimePrototype

from the_tale.game.persons.storage import persons_storage
from the_tale.game.persons.conf import persons_settings

from the_tale.game.map import logic as map_logic

from the_tale.game.map.places.prototypes import PlacePrototype
from the_tale.game.map.places.conf import places_settings
from the_tale.game.map.places import exceptions
from the_tale.game.map.places.storage import places_storage

class PlacePowerTest(testcase.TestCase):

    def setUp(self):
        super(PlacePowerTest, self).setUp()
        linguistics_logic.sync_static_restrictions()

        map_logic.create_test_my_info()

        places_storage.clear()
        persons_storage.clear()

        self.place = PlacePrototype.create(x=0,
                                           y=0,
                                           size=5,
                                           utg_name=names.generator.get_test_name(name='power_test_place'),
                                           race=RACE.HUMAN)

        self.place.sync_persons(force_add=True)

        persons_storage.sync(force=True)

    def test_initialization(self):
        self.assertEqual(self.place.power, 0)

    def test_push_power(self):
        self.place.push_power(0, 10)
        self.assertEqual(self.place.power, 10)

        TimePrototype.get_current_time().increment_turn()
        self.place.push_power(1, 1)
        self.assertEqual(self.place.power,
                         1 + 10*float(places_settings.POWER_HISTORY_LENGTH-1)/places_settings.POWER_HISTORY_LENGTH)

        TimePrototype(places_settings.POWER_HISTORY_LENGTH-1).save()
        self.place.push_power(places_settings.POWER_HISTORY_LENGTH-1, 100)
        self.assertEqual(self.place.power,
                         100 + 10*1.0/places_settings.POWER_HISTORY_LENGTH + 2.0/places_settings.POWER_HISTORY_LENGTH)

        TimePrototype(places_settings.POWER_HISTORY_LENGTH).save()
        self.place.push_power(places_settings.POWER_HISTORY_LENGTH, 1000)
        self.assertEqual(self.place.power,
                         1000 + 100*float(places_settings.POWER_HISTORY_LENGTH-1)/places_settings.POWER_HISTORY_LENGTH + 1.0/places_settings.POWER_HISTORY_LENGTH)

        TimePrototype(places_settings.POWER_HISTORY_LENGTH+1).save()
        self.place.push_power(places_settings.POWER_HISTORY_LENGTH+1, 10000)
        self.assertEqual(self.place.power,
                         10000 +
                         1000*float(places_settings.POWER_HISTORY_LENGTH-1)/places_settings.POWER_HISTORY_LENGTH +
                         100*float(places_settings.POWER_HISTORY_LENGTH-2)/places_settings.POWER_HISTORY_LENGTH)

        TimePrototype(places_settings.POWER_HISTORY_LENGTH+2).save()
        self.place.push_power(places_settings.POWER_HISTORY_LENGTH+2, 100000)
        self.assertEqual(round(self.place.power, 5),
                         round(100000 +
                               10000*float(places_settings.POWER_HISTORY_LENGTH-1)/places_settings.POWER_HISTORY_LENGTH +
                               1000*float(places_settings.POWER_HISTORY_LENGTH-2)/places_settings.POWER_HISTORY_LENGTH +
                               100*float(places_settings.POWER_HISTORY_LENGTH-3)/places_settings.POWER_HISTORY_LENGTH, 5) )

    def test_push_power_exceptions(self):
        self.place.push_power(666, 10)
        self.assertRaises(exceptions.PlacesPowerError, self.place.push_power, 13, 1)

    def test_persons_sorting(self):
        person_1 = self.place.persons[0]
        person_2 = self.place.persons[1]

        person_1.push_power(0, 1)
        person_1.save()

        person_2.push_power(0, 10)
        person_2.save()

        self.assertEqual([person.id for person in self.place.persons][:2],
                         [person_2.id, person_1.id])

    def test_sync_persons_add_new_person(self):
        persons = self.place.persons
        removed_person = persons[-1]
        removed_person.move_out_game()
        self.place.sync_persons(force_add=True)
        self.assertEqual([p.id for p in persons[:-1]], [p.id for p in self.place.persons[:-1]])
        self.assertNotEqual(removed_person.id, self.place.persons[-1].id)

    @mock.patch('the_tale.game.map.places.prototypes.PlacePrototype.max_persons_number', 10)
    def test_sync_persons_add_new_person__force_when_zero_persons(self):
        TimePrototype.get_current_time().increment_turn()

        self.assertEqual(self.place.persons_changed_at_turn, 0)
        self.assertFalse(self.place.can_add_person)

        old_persons = self.place.persons

        for person in self.place.persons:
            person.move_out_game()

        self.place.sync_persons(force_add=False)

        self.assertEqual(self.place.persons_changed_at_turn, TimePrototype.get_current_turn_number())
        self.assertEqual(len(self.place.persons), 1)
        self.assertFalse(self.place.persons[0] in old_persons)

    @mock.patch('the_tale.game.map.places.prototypes.PlacePrototype.max_persons_number', 100)
    def test_sync_persons_add_new_person__add_delay(self):
        self.assertEqual(self.place.persons_changed_at_turn, 0)
        self.assertFalse(self.place.can_add_person)

        old_persons = self.place.persons

        self.place.sync_persons(force_add=False)

        self.assertEqual(old_persons, self.place.persons)


    def test_sync_persons_remove_unstable_person(self):
        persons = self.place.persons
        unstable_person = persons[-1]
        unstable_person._model.created_at_turn -= persons_settings.POWER_STABILITY_WEEKS*7*24*c.TURNS_IN_HOUR+1
        self.place.sync_persons(force_add=True)
        self.assertEqual([p.id for p in persons[:-1]], [p.id for p in self.place.persons[:-1]])
        self.assertNotEqual(unstable_person.id, self.place.persons[-1].id)
