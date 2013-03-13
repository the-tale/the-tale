# coding: utf-8
import math

from deworld.layers import VEGETATION_TYPE

from common.utils import xls

from game.map.conf import map_settings
from game.map.relations import TERRAIN


_xls_attributes = {'filename': map_settings.TERRAIN_PRIORITIES_FIXTURE,
                   'rows': list(TERRAIN._STR_TO_ID.keys()) } # ['%.1f' % (val/10.0) for val in xrange(-10, 10)]

_modify_row_names = lambda d: dict((TERRAIN._STR_TO_ID[key], value) for key, value in d.items())

_HEIGHT_POINTS = _modify_row_names(xls.load_table(sheet_index=0, columns=[ round(val/10.0, 1) for val in xrange(-10, 11)], **_xls_attributes))
_TEMPERATURE_POINTS = _modify_row_names(xls.load_table(sheet_index=1, columns=[ round(val/10.0, 1) for val in xrange(0, 11)], **_xls_attributes))
_WETNESS_POINTS = _modify_row_names(xls.load_table(sheet_index=2, columns=[ round(val/10.0, 1) for val in xrange(0, 11)], **_xls_attributes))
_VEGETATION_POINTS = _modify_row_names(xls.load_table(sheet_index=3, columns=['DESERT', 'GRASS', 'FOREST'], **_xls_attributes))
_SOIL_POINTS = _modify_row_names(xls.load_table(sheet_index=4, columns=[ round(val/10.0, 1) for val in xrange(0, 11)], **_xls_attributes))

def mid(left, right, x, left_value, right_value):
    if left == right: return left_value
    # return ( (x - left) * left_value + (right - x) * right_value) / (right - left)

    return (right_value - left_value) * (x - left) / (right - left) + left_value

class Biom(object):

    def __init__(self, id_):
        self.id = id_

    def _cell_mid(self, value, min_, max_, data):
        left = math.floor(value*10)/10.0
        right = math.ceil(value*10)/10.0

        if left < min_: left = min_
        if right > max_: right = max_

        return mid(left, right, value, data[self.id][left], data[self.id][right])

    def height_points(self, cell): return self._cell_mid(cell.height, -1, 1, _HEIGHT_POINTS)
    def temperature_points(self, cell): return self._cell_mid(cell.temperature, 0, 1, _TEMPERATURE_POINTS)
    def wetness_points(self, cell): return self._cell_mid(cell.wetness, 0, 1, _WETNESS_POINTS)

    def vegetation_points(self, cell): return _VEGETATION_POINTS[self.id][{VEGETATION_TYPE.DESERT: 'DESERT',
                                                                           VEGETATION_TYPE.GRASS: 'GRASS',
                                                                           VEGETATION_TYPE.FOREST: 'FOREST'}[cell.vegetation]]

    def soil_points(self, cell): return self._cell_mid(cell.soil, 0, 1, _SOIL_POINTS)

    def check(self, cell):
        return ( self.height_points(cell) +
                 self.temperature_points(cell) +
                 self.wetness_points(cell) +
                 self.vegetation_points(cell) +
                 self.soil_points(cell))

    def get_points(self, cell):
        return [ ('height', self.height_points(cell)),
                 ('temperature', self.temperature_points(cell)),
                 ('wetness', self.wetness_points(cell)),
                 ('vegetation', self.vegetation_points(cell)),
                 ('soil', self.soil_points(cell)) ]
