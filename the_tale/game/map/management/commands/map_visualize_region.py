# coding: utf-8

import json

import PIL

from optparse import make_option

from django.core.management.base import BaseCommand

from the_tale.common.utils.logic import run_django_command

from the_tale.game.map.relations import SPRITES
from the_tale.game.map.storage import map_info_storage
from the_tale.game.map.conf import map_settings


OUTPUT_RECTANGLE = (8*map_settings.CELL_SIZE, 1*map_settings.CELL_SIZE, 50*map_settings.CELL_SIZE, 36*map_settings.CELL_SIZE)

REAL_SIZE = ((OUTPUT_RECTANGLE[2]-OUTPUT_RECTANGLE[0]),
             (OUTPUT_RECTANGLE[3]-OUTPUT_RECTANGLE[1]))


def draw_sprite(image, texture, sprite_info, x, y, rotate=0, base=False):

    sprite_borders = (sprite_info.x, sprite_info.y,
                      sprite_info.x + map_settings.CELL_SIZE, sprite_info.y + map_settings.CELL_SIZE)

    sprite = texture.crop(sprite_borders)

    if rotate:
        sprite = sprite.rotate(-rotate)

    image.paste(sprite, (x * map_settings.CELL_SIZE, y * map_settings.CELL_SIZE), sprite)



class Command(BaseCommand):

    help = 'visualize map with region data'

    requires_model_validation = False

    option_list = BaseCommand.option_list + ( make_option('-r', '--region',
                                                          action='store',
                                                          type=str,
                                                          dest='region',
                                                          help='region file name'),
                                              make_option('-o', '--output',
                                                          action='store',
                                                          type=str,
                                                          dest='output',
                                                          help='output file'),)


    def handle(self, *args, **options):

        region = options['region']
        if not region:
            region = map_settings.GEN_REGION_OUTPUT % map_info_storage.version

        output = options['output']
        if not output:
            output = '/tmp/the-tale-map.png'

        with open(region) as region_file:
            data = json.loads(region_file.read())

        format_version = data.get('format_version')

        if format_version is None:
            run_django_command(['map_visualize_old_region', '-r', region, '-o', output])
            return

        draw_info = data['draw_info']

        width = data['width']
        height = data['height']

        image = PIL.Image.new('RGBA', (width*map_settings.CELL_SIZE, height*map_settings.CELL_SIZE))

        texture = PIL.Image.open(map_settings.TEXTURE_PATH)

        for y, row in enumerate(draw_info):
            for x, cell in enumerate(row):
                sprites = cell if isinstance(cell, list) else [cell]
                for sprite in sprites:
                    rotate = 0
                    if isinstance(sprite, list):
                        sprite, rotate = sprite
                    draw_sprite(image, texture, SPRITES(sprite), x, y, rotate=rotate)

        image.crop(OUTPUT_RECTANGLE).resize(REAL_SIZE, PIL.Image.ANTIALIAS).save(output)
