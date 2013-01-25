# -*- coding: utf-8 -*-
import subprocess

from django.core.management.base import BaseCommand

from dext.utils.decorators import nested_commit_on_success

from game.map.roads.models import Road
from game.map.places.models import Place, PLACE_TYPE
from game.map.places.storage import places_storage
from game.map.roads.storage import roads_storage

class Command(BaseCommand):

    help = 'create test map'

    def handle(self, *args, **options):

        self.create_map()

        subprocess.call(['./manage.py', 'map_update_map'])



    def create_place(self, x, y, size):
        return Place.objects.create( x=x,
                                     y=y,
                                     name='%dx%d' % (x, y),
                                     type=PLACE_TYPE.CITY,
                                     size=size)

    def create_road(self, p1, p2):
        return Road.objects.create(point_1=p1, point_2=p2)


    @nested_commit_on_success
    def create_map(self):

        Place.objects.all().delete()
        Road.objects.all().delete()

        p1x1   = self.create_place(1,  1,  size=1)
        p14x1  = self.create_place(14, 1,  size=1)
        p27x1  = self.create_place(27, 1,  size=6)
        p5x3   = self.create_place(5,  3,  size=5)
        p1x9   = self.create_place(1,  9,  size=6)
        p5x12  = self.create_place(5,  12, size=1)
        p3x17  = self.create_place(3,  17, size=10)
        p10x18 = self.create_place(10, 18, size=3)
        p11x11 = self.create_place(11, 11, size=4)
        p11x6  = self.create_place(11, 6,  size=4)
        p19x5  = self.create_place(19, 5,  size=3)
        p20x8  = self.create_place(20, 8,  size=9)
        p24x8  = self.create_place(24, 8,  size=10)
        p17x12 = self.create_place(17, 12, size=2)
        p19x17 = self.create_place(19, 17, size=8)
        p24x13 = self.create_place(24, 13, size=1)
        p27x13 = self.create_place(27, 13, size=1)
        p28x19 = self.create_place(28, 19, size=3)

        self.create_road(p1x1,   p5x3)
        self.create_road(p5x3,   p1x9)
        self.create_road(p5x3,   p11x6)
        self.create_road(p1x9,   p5x12)
        self.create_road(p5x12,  p3x17)
        self.create_road(p5x12,  p11x11)
        self.create_road(p3x17,  p10x18)
        self.create_road(p11x11, p10x18)
        self.create_road(p11x11, p11x6)
        self.create_road(p11x11, p19x17)
        self.create_road(p11x11, p17x12)
        self.create_road(p11x11, p20x8)
        self.create_road(p11x6,  p14x1)
        self.create_road(p14x1,  p27x1)
        self.create_road(p27x1,  p24x8)
        self.create_road(p24x8,  p20x8)
        self.create_road(p24x8,  p24x13)
        self.create_road(p24x8,  p27x13)
        self.create_road(p20x8,  p19x5)
        self.create_road(p20x8,  p17x12)
        self.create_road(p19x17, p24x13)
        self.create_road(p28x19, p24x13)
        self.create_road(p28x19, p27x13)

        places_storage.update_version()
        places_storage.sync(force=True)

        roads_storage.update_version()
        roads_storage.sync(force=True)
