
import smart_imports

smart_imports.all()


OUTPUT_RECTANGLE = (8 * conf.settings.CELL_SIZE, 1 * conf.settings.CELL_SIZE, 50 * conf.settings.CELL_SIZE, 36 * conf.settings.CELL_SIZE)

REAL_SIZE = ((OUTPUT_RECTANGLE[2] - OUTPUT_RECTANGLE[0]),
             (OUTPUT_RECTANGLE[3] - OUTPUT_RECTANGLE[1]))


def draw_sprite(image, texture, sprite_info, x, y, rotate=0, base=False):

    sprite_borders = (sprite_info.x, sprite_info.y,
                      sprite_info.x + conf.settings.CELL_SIZE, sprite_info.y + conf.settings.CELL_SIZE)

    sprite = texture.crop(sprite_borders)

    if rotate:
        sprite = sprite.rotate(-rotate)

    image.paste(sprite, (x * conf.settings.CELL_SIZE, y * conf.settings.CELL_SIZE), sprite)


class Command(django_management.BaseCommand):

    help = 'visualize map with region data'

    requires_model_validation = False

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument('-r', '--region', action='store', type=str, dest='region', help='region file name')
        parser.add_argument('-o', '--output', action='store', type=str, dest='output', help='output file')

    def handle(self, *args, **options):

        region = options['region']
        if not region:
            region = conf.settings.GEN_REGION_OUTPUT % storage.map_info.version

        output = options['output']
        if not output:
            output = '/tmp/the-tale-map.png'

        with open(region) as region_file:
            data = json.loads(region_file.read())

        format_version = data.get('format_version')

        if format_version is None:
            utils_logic.run_django_command(['map_visualize_old_region', '-r', region, '-o', output])
            return

        draw_info = data['draw_info']

        width = data['width']
        height = data['height']

        image = PIL.Image.new('RGBA', (width * conf.settings.CELL_SIZE, height * conf.settings.CELL_SIZE))

        texture = PIL.Image.open(conf.settings.TEXTURE_PATH)

        for y, row in enumerate(draw_info):
            for x, cell in enumerate(row):
                sprites = cell if isinstance(cell, list) else [cell]
                for sprite in sprites:
                    rotate = 0
                    if isinstance(sprite, list):
                        sprite, rotate = sprite
                    draw_sprite(image, texture, relations.SPRITES(sprite), x, y, rotate=rotate)

        image.crop(OUTPUT_RECTANGLE).resize(REAL_SIZE, PIL.Image.ANTIALIAS).save(output)
