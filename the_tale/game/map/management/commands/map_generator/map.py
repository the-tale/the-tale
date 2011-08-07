# -*- coding: utf-8 -*-
import math
from ....places.models import TERRAIN

class MapGeneratorException(Exception): pass

class Cell(object):
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.terrains = {}
        self.terrain = TERRAIN.GRASS

    def update_terrain(self, terrain, power):
        self.terrains[terrain] = self.terrains.get(terrain, 0) + power

    def choose_terrain(self):
        cur_power = -1
        for terrain, power in self.terrains.items():
            if power > cur_power:
                cur_power = power
                self.terrain = terrain
            
    def __repr__(self):
        return 'Cell(%i, %i)' % (self.x, self.y)


class Map(object):

    def __init__(self, w, h):
        self.w = w
        self.h = h
        
        self.map = [ [Cell(x, y) for x in xrange(w)] for y in xrange(h)]

        self.places = {}

    def add_place(self, place):
        if place.id in self.places:
            raise MapGeneratorException('place with id "%i" has already exists' % place.id)

        self.places[place.id] = place

        self.update_terrain(place.x, place.y, place.significance, place.terrain)


    def update_terrain(self, center_x, center_y, significance, terrain):
        
        sig_radius = int(significance)

        for y in xrange(center_y - sig_radius, center_y + sig_radius):
            for x in xrange(center_x - sig_radius, center_x + sig_radius):
                distance = math.sqrt( math.pow(y - center_y, 2) + math.pow(x - center_x, 2))
                if 0 <= y < self.h and 0 <= x < self.w:
                    self.map[y][x].update_terrain(terrain, max(0, sig_radius - distance) )

    def prepair_terrain(self):
        for row in self.map:
            for cell in row:
                cell.choose_terrain()

    def get_terrain_map(self):
        return [ [cell.terrain for cell in row] for row in self.map]

    def get_json_region_data(self):
        data = {}

        data['width'] = self.w
        data['height'] = self.h
        data['terrain'] = [ ''.join(row) for row in self.get_terrain_map() ]
        data['places'] = [ place.get_json_data() for place in self.places.values() ] 

        return data

    def __repr__(self):
        return '%r' % self.map

    ####################################
    # for debug purpose
    ####################################

    def print_terrain_map(self):
        for row in self.get_terrain_map():
            print ''.join(row)     

