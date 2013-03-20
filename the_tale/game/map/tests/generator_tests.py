# coding: utf-8

# coding: utf-8

from common.utils.testcase import TestCase

from game.logic import create_test_map


from game.map.places.prototypes import BuildingPrototype
from game.map.places.relations import BUILDING_TYPE
from game.map.generator.power_points import get_building_power_points


class GeneratorTests(TestCase):

    def setUp(self):
        super(GeneratorTests, self).setUp()
        self.place_1, self.place_2, self.place_3 = create_test_map()



def create_test_building_power_point(building_type):

    def test_building_power_point(self):
        building = BuildingPrototype.create(self.place_1.persons[0])
        building._model.type = building_type
        building.save()

        self.assertTrue(len(get_building_power_points(building)) > 0)

    return test_building_power_point



for record in BUILDING_TYPE._records:

    method = create_test_building_power_point(record)
    setattr(GeneratorTests, 'test_%s' % record.name, method)
