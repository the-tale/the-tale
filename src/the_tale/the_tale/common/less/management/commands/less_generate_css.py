
import smart_imports

smart_imports.all()


class Command(utilities_base.Command):

    help = 'generate css from less sources'

    LOCKS = []

    GAME_CAN_BE_IN_MAINTENANCE_MODE = True

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument('-o',
                            '--output',
                            action='store',
                            type=str,
                            dest='output',
                            help='output directory',
                            default=django_settings.LESS_OUTPUT_DIR)

    def _handle(self, *args, **options):

        output_dir = options['output']

        self.logger.info('source dir: %s' % django_settings.LESS_FILES_DIR)
        self.logger.info('destination dir: %s' % output_dir)

        self.logger.info('remove old data')

        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)

        if not os.path.exists(output_dir):
            os.mkdir(output_dir)

        self.logger.info('generate new data')

        norm_source_path = os.path.abspath(django_settings.LESS_FILES_DIR)

        for dirpath, dirnames, filenames in os.walk(django_settings.LESS_FILES_DIR):
            norm_path = os.path.abspath(dirpath)

            rel_path = os.path.relpath(norm_path, norm_source_path)
            dest_dir = os.path.join(output_dir, rel_path)

            if not os.path.isdir(dest_dir):
                os.mkdir(dest_dir)

            for filename in filenames:
                if filenames[0] == '.':
                    continue
                src_file =  os.path.join(norm_path, filename)
                dest_file = os.path.join(dest_dir, filename)

                self.logger.info('process file: %s' % src_file)

                if not src_file.endswith('.less'):

                    if src_file.endswith('.css'):
                        shutil.copy(src_file, dest_file)
                        self.logger.info('...copy')

                    self.logger.info('...skeep')
                    continue

                self.logger.info('...generate')

                dest_file = dest_file[:-5] + '.css'

                f = open(dest_file, 'w')
                (out, err) = subprocess.Popen(["lessc", src_file], stdout=f).communicate()
                f.close()

        self.logger.info('all files processed')
