# coding: utf-8
import mock

from the_tale.common.utils import testcase

from the_tale.linguistics import logic as linguistics_logic

from the_tale.game import names

from the_tale.game.balance import constants as c
from the_tale.game.relations import RACE
from the_tale.game.prototypes import TimePrototype

from the_tale.game.persons import storage as persons_storage

from the_tale.game.map import logic as map_logic

from .. import logic
from .. import exceptions
from .. import storage


class PlacePowerTest(testcase.TestCase):

    def setUp(self):
        super(PlacePowerTest, self).setUp()
        linguistics_logic.sync_static_restrictions()

        map_logic.create_test_map_info()

        storage.places.clear()
        persons_storage.persons.clear()

        self.place = logic.create_place(x=0,
                                        y=0,
                                        size=5,
                                        utg_name=names.generator.get_test_name(name='power_test_place'),
                                        race=RACE.HUMAN)

        for i in xrange(3):
            logic.add_person_to_place(self.place)

        persons_storage.persons.sync(force=True)

    def test_inner_circle_size(self):
        self.assertEqual(self.place.politic_power.INNER_CIRCLE_SIZE, 7)


    def test_initialization(self):
        self.assertEqual(self.place.total_politic_power_fraction, 0)


    @mock.patch('the_tale.game.places.attributes.Attributes.freedom', 0.5)
    def test_change_power(self):
        with mock.patch('the_tale.game.politic_power.PoliticPower.change_power') as change_power:
            self.assertEqual(self.place.politic_power.change_power(place=self.place,
                                                                   hero_id=None,
                                                                   has_in_preferences=False,
                                                                   power=1000),
                             None)

        self.assertEqual(change_power.call_args,
                         mock.call(owner=self.place,
                                   hero_id=None,
                                   has_in_preferences=False,
                                   power=500))
