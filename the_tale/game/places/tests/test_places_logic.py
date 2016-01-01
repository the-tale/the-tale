# coding: utf-8

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

        map_logic.create_test_my_info()

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

    def test_initialization(self):
        self.assertEqual(self.place.power, 0)
