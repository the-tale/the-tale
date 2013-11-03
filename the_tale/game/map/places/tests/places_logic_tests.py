# coding: utf-8

from the_tale.common.utils import testcase

from textgen import words
from dext.utils import s11n

from the_tale.game.balance import constants as c
from the_tale.game.relations import RACE

from the_tale.game.persons.storage import persons_storage
from the_tale.game.persons.conf import persons_settings

from the_tale.game.map.places.prototypes import PlacePrototype
from the_tale.game.map.places.models import Place
from the_tale.game.map.places.conf import places_settings
from the_tale.game.map.places.exceptions import PlacesException
from the_tale.game.map.places.storage import places_storage

class PlacePowerTest(testcase.TestCase):

    def setUp(self):
        super(PlacePowerTest, self).setUp()
        places_storage.clear()
        persons_storage.clear()

        self.model = Place.objects.create(x=0,
                                          y=0,
                                          name='power_test_place',
                                          name_forms=s11n.to_json(words.Noun.fast_construct('power_test_place').serialize()),
                                          race=RACE.HUMAN,
                                          size=5 )

        self.place = PlacePrototype(self.model)
        self.place.sync_persons()

        places_storage.sync(force=True)
        persons_storage.sync(force=True)


    def test_initialization(self):
        self.assertEqual(self.place.power, 0)

    def test_push_power(self):
        self.place.push_power(0, 10)
        self.assertEqual(self.place.power, 10)

        self.place.push_power(1, 1)
        self.assertEqual(self.place.power, 11)

        self.place.push_power(places_settings.POWER_HISTORY_LENGTH-1, 100)
        self.assertEqual(self.place.power, 111)

        self.place.push_power(places_settings.POWER_HISTORY_LENGTH, 1000)
        self.assertEqual(self.place.power, 1111)

        self.place.push_power(places_settings.POWER_HISTORY_LENGTH+1, 10000)
        self.assertEqual(self.place.power, 11101)

        self.place.push_power(places_settings.POWER_HISTORY_LENGTH+2, 100000)
        self.assertEqual(self.place.power, 111100)

    def test_push_power_exceptions(self):
        self.place.push_power(666, 10)
        self.assertRaises(PlacesException, self.place.push_power, 13, 1)

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
        self.place.sync_persons()
        self.assertEqual([p.id for p in persons[:-1]], [p.id for p in self.place.persons[:-1]])
        self.assertNotEqual(removed_person.id, self.place.persons[-1].id)

    def test_sync_persons_remove_unstable_person(self):
        persons = self.place.persons
        unstable_person = persons[-1]
        unstable_person._model.created_at_turn -= persons_settings.POWER_STABILITY_WEEKS*7*24*c.TURNS_IN_HOUR+1
        self.place.sync_persons()
        self.assertEqual([p.id for p in persons[:-1]], [p.id for p in self.place.persons[:-1]])
        self.assertNotEqual(unstable_person.id, self.place.persons[-1].id)
