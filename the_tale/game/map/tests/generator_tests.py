# coding: utf-8
import random

from textgen.words import Noun

from common.utils.testcase import TestCase

from game.logic import create_test_map

from game.map.places.prototypes import BuildingPrototype
from game.map.places.relations import BUILDING_TYPE
from game.map.generator.power_points import get_building_power_points
from game.map.generator.descriptors import UICell, UICells
from game.map.storage import map_info_storage
from game.map.prototypes import WorldInfoPrototype


class GeneratorTests(TestCase):

    def setUp(self):
        super(GeneratorTests, self).setUp()
        self.place_1, self.place_2, self.place_3 = create_test_map()

    def test_ui_cell_serialization(self):
        generator = WorldInfoPrototype.get_by_id(map_info_storage.item.world_id).generator

        world_cell = generator.cell_info(random.randint(0, generator.w-1), random.randint(0, generator.h-1))

        ui_cell = UICell(world_cell)

        self.assertEqual(ui_cell.serialize(), UICell.deserialize(ui_cell.serialize()).serialize())

    def test_ui_cells_serialization(self):
        generator = WorldInfoPrototype.get_by_id(map_info_storage.item.world_id).generator

        cells = UICells(generator)

        self.assertEqual(cells.serialize(), UICells.deserialize(cells.serialize()).serialize())


def create_test_building_power_point(building_type):

    def test_building_power_point(self):
        building = BuildingPrototype.create(self.place_1.persons[0], name_forms=Noun.fast_construct('building-name'))
        building._model.type = building_type
        building.save()

        self.assertTrue(len(get_building_power_points(building)) > 0)

    return test_building_power_point



for record in BUILDING_TYPE._records:

    method = create_test_building_power_point(record)
    setattr(GeneratorTests, 'test_%s' % record.name, method)
