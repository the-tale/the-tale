
import smart_imports

smart_imports.all()


CELL_SIZE = 32

TEXTURE_PATH = '/home/tie/repos/mine/the-tale/the_tale/static/game/images/map.png'


class Command(django_management.BaseCommand):

    help = 'make map changing video from region datas'

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument('-r', '--regions', action='store', type=str, dest='regions', default=map_conf.settings.GEN_MAP_DIR, help='region file name')
        parser.add_argument('-o', '--output', action='store', type=str, dest='output', help='output file')

    def handle(self, *args, **options):
        regions_dir = options['regions']

        output = options['output']
        if not output:
            output = '/home/tie/tmp/m.mp4'

        print('REGIONS DIR: %s' % regions_dir)

        regions = sorted([os.path.join(regions_dir, filename)
                          for filename in os.listdir(regions_dir)
                          if os.path.isfile(os.path.join(regions_dir, filename)) and filename.startswith('region-')])

        temp_dir = tempfile.mkdtemp(prefix='the-tale-map-viz')

        # temp_dir = '/tmp/the-tale-map-viz3yLsjQ'

        print('TEMP DIR: %s' % temp_dir)

        print('FOUND %d regions' % len(regions))

        for i, region_filename in enumerate(regions):
            print('process region %d: %s' % (i, region_filename))
            output_file = os.path.join(temp_dir, '%.10d.png' % i)
            dext_logic.run_django_command(['map_visualize_region', '-r', region_filename, '-o', output_file])

        if os.path.exists(output):
            os.remove(output)

        subprocess.call(['ffmpeg', '-i', os.path.join(temp_dir, '%10d.png'), '-sameq', output])

        # shutil.rmtree(temp_dir.name)
