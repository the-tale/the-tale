# coding: utf-8


from optparse import make_option

from django.core.management.base import BaseCommand

# from game.prototypes import TimePrototype

from game.map.storage import map_info_storage
from game.map.prototypes import WorldInfoPrototype



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


    def handle(self, *args, **options):

        x = options['x']
        y = options['y']

        generator = WorldInfoPrototype.get_by_id(map_info_storage.item.world_id).generator

        cell = generator.cell_info(x, y)
        power_cell = generator.cell_power_info(x, y)

        print '----CELL--%d--%d--' % (x, y)
        print 'height:            %.2f \t\t| %r       ' % (cell.height, power_cell.height)
        print 'temperature:       %.2f \t\t| %f       ' % (cell.temperature, power_cell.temperature)
        print 'wind:              (%.2f, %.2f) \t| %r ' % (cell.wind[0], cell.wind[1], power_cell.wind)
        print 'wetness:           %.2f \t\t| %f       ' % (cell.wetness, power_cell.wetness)
        print 'vegetation:        %.2f \t\t| %r       ' % (cell.vegetation, power_cell.vegetation)
        print 'soil:              %.2f \t\t| %f       ' % (cell.soil, power_cell.soil)
        print 'atmo_wind:         (%.2f, %.2f) \t|    ' % cell.atmo_wind
        print 'atmo_temperature:  %.2f \t\t|          ' % (cell.atmo_temperature,)
        print 'atmo_wetness:      %.2f \t\t|          ' % (cell.atmo_wetness,)
