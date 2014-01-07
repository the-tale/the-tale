# coding: utf-8

from django.core.management.base import BaseCommand
from django.db import transaction

from the_tale.common.utils.logic import run_django_command

from the_tale.game.persons.storage import persons_storage

from the_tale.game.map.roads.models import Road
from the_tale.game.map.places.models import Place
from the_tale.game.map.relations import TERRAIN
from the_tale.game.map.places.storage import places_storage
from the_tale.game.map.roads.storage import roads_storage
from the_tale.game.map.storage import map_info_storage
from the_tale.game.map.prototypes import MapInfoPrototype, WorldInfoPrototype
from the_tale.game.map.conf import map_settings

class Command(BaseCommand):

    help = 'create test map'

    def handle(self, *args, **options):

        self.create_map()

        run_django_command(['map_update_map'])



    def create_place(self, x, y, size):
        return Place.objects.create( x=x,
                                     y=y,
                                     name='%dx%d' % (x, y),
                                     size=size)

    def create_road(self, p1, p2):
        return Road.objects.create(point_1=p1, point_2=p2)


    @transaction.atomic
    def create_map(self): # pylint: disable=R0914, R0915

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
        roads_storage.update_version()

        for place in places_storage.all():
            place.sync_persons(force_add=True)

        persons_storage.update_version()

        terrain = []
        for y in xrange(0, map_settings.HEIGHT): # pylint: disable=W0612
            row = []
            terrain.append(row)
            for x in xrange(0, map_settings.WIDTH): # pylint: disable=W0612
                row.append(TERRAIN.PLANE_GREENWOOD)

        map_info_storage.set_item(MapInfoPrototype.create(turn_number=0,
                                                          width=map_settings.WIDTH,
                                                          height=map_settings.HEIGHT,
                                                          terrain=terrain,
                                                          world=WorldInfoPrototype.create(w=map_settings.WIDTH, h=map_settings.HEIGHT)))

        map_info_storage.update_version()
