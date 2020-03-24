
import smart_imports

smart_imports.all()


class Command(utilities_base.Command):

    help = 'make map changing video from region datas'

    LOCKS = ['game_commands']

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument('-i', '--images', action='store', type=str, dest='images', help='directory with images')
        parser.add_argument('-o', '--output', action='store', type=str, dest='output', help='output file')

    def _handle(self, *args, **options):

        images_dir = options['images']

        output = options['output']

        self.logger.info('IMAGES DIR: %s' % images_dir)

        regions_number = models.MapRegion.objects.all().count()

        self.logger.info('FOUND %d regions' % regions_number)

        for i, region in enumerate(models.MapRegion.objects.all().order_by('turn_number').iterator()):
            self.logger.info(f'process turn {region.turn_number}, {i} / {regions_number} {i/regions_number*100:.2f}%')
            output_file = os.path.join(images_dir, '%.10d.png' % i)
            visualization.draw(region.data, output_file)

        if os.path.exists(output):
            os.remove(output)

        # subprocess.call(['ffmpeg', '-i', os.path.join(images_dir, '%10d.png'), '-sameq', output])

        # shutil.rmtree(images_dir.name)
