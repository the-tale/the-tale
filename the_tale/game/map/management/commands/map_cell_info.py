# coding: utf-8


from optparse import make_option

from django.core.management.base import BaseCommand

# from the_tale.game.prototypes import TimePrototype

from the_tale.game.map.relations import TERRAIN
from the_tale.game.map.storage import map_info_storage
from the_tale.game.map.prototypes import WorldInfoPrototype
from the_tale.game.map.generator.biomes import Biom
from the_tale.game.map.generator.power_points import get_power_points


class Command(BaseCommand):

    help = 'generate map'

    requires_model_validation = False

    option_list = BaseCommand.option_list + ( make_option('-x',
                                                          action='store',
                                                          type=int,
                                                          dest='x',
                                                          default=None,
                                                          help='x coordinate'),

                                              make_option('-y',
                                                          action='store',
                                                          type=int,
                                                          dest='y',
                                                          default=None,
                                                          help='y coordinate'), )


    def handle(self, *args, **options): # pylint: disable=R0914

        x = options['x']
        y = options['y']

        generator = WorldInfoPrototype.get_by_id(map_info_storage.item.world_id).generator

        cell = generator.cell_info(x, y)
        power_cell = generator.cell_power_info(x, y)

        print '----CELL--x=%d--y=%d--' % (x, y)
        print 'height:            %.2f \t\t| %r       ' % (cell.height, power_cell.height)
        print 'temperature:       %.2f \t\t| %f       ' % (cell.temperature, power_cell.temperature)
        print 'wind:              (%.2f, %.2f) \t| %r ' % (cell.wind[0], cell.wind[1], power_cell.wind)
        print 'wetness:           %.2f \t\t| %f       ' % (cell.wetness, power_cell.wetness)
        print 'vegetation:        %.2f \t\t| %r       ' % (cell.vegetation, power_cell.vegetation)
        print 'soil:              %.2f \t\t| %f       ' % (cell.soil, power_cell.soil)
        print 'atmo_wind:         (%.2f, %.2f) \t|    ' % cell.atmo_wind
        print 'atmo_temperature:  %.2f \t\t|          ' % (cell.atmo_temperature,)
        print 'atmo_wetness:      %.2f \t\t|          ' % (cell.atmo_wetness,)

        terrain_points = []
        for terrain_id, text in TERRAIN._ID_TO_TEXT.items():
            biom = Biom(id_=terrain_id)
            terrain_points.append((text, biom.check(cell), biom.get_points(cell)))
        terrain_points = sorted(terrain_points, key=lambda x: -x[1])

        print
        print '----TERRAIN----'
        for biom_name, total_power, aspects in terrain_points[:5]:
            print '%.2f\t%s' % (total_power, biom_name)

            for aspect_name, aspect_value in aspects:
                print '\t%.2f\t%s' % (aspect_value, aspect_name)

        print
        print '----POINTS----'

        points = []
        for point in get_power_points():
            value = point.log_powers_for(generator, x=x, y=y)
            if value:
                points.append((point.name, value))
        points.sort()

        for name, value in points:
            print '%s %r' % (name.ljust(35), value)
