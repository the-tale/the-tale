# coding: utf-8

from deworld.layers import VEGETATION_TYPE


class BiomBase(object):

    def __init__(self, id_):
        self.id = id_

    def check(self, cell):
        return False


class Default(BiomBase):

    def check(self, cell):
        return True


class Swamp(BiomBase):

    def check(self, cell):
        return ( cell.height < -0.3 or
                 cell.wetness > 0.8 or
                 (cell.height < 0 and cell.wetness > 0.6))

class Grass(BiomBase):

    def check(self, cell):
        return cell.vegetation == VEGETATION_TYPE.GRASS


class Forest(BiomBase):

    def check(self, cell):
        return cell.vegetation == VEGETATION_TYPE.FOREST


class Mountains(BiomBase):

    def check(self, cell):
        return cell.height > 0.3


class Desert(BiomBase):

    def check(self, cell):
        return ( cell.temperature > 0.8 or
                 cell.vegetation == VEGETATION_TYPE.DESERT )
