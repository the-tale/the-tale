
import smart_imports

smart_imports.all()


class Command(django_management.BaseCommand):

    help = 'generate css from less sources'

    def handle(self, *args, **options):

        print('source dir: %s' % django_settings.LESS_FILES_DIR)
        print('destination dir: %s' % django_settings.LESS_DEST_DIR)

        print('remove old data')
        if os.path.exists(django_settings.LESS_DEST_DIR):
            shutil.rmtree(django_settings.LESS_DEST_DIR)

        if not os.path.exists(django_settings.LESS_DEST_DIR):
            os.mkdir(django_settings.LESS_DEST_DIR)

        print('generate new data')

        norm_source_path = os.path.abspath(django_settings.LESS_FILES_DIR)

        for dirpath, dirnames, filenames in os.walk(django_settings.LESS_FILES_DIR):
            norm_path = os.path.abspath(dirpath)

            rel_path = os.path.relpath(norm_path, norm_source_path)
            dest_dir = os.path.join(django_settings.LESS_DEST_DIR, rel_path)

            if not os.path.isdir(dest_dir):
                os.mkdir(dest_dir)

            for filename in filenames:
                if filenames[0] == '.':
                    continue
                src_file =  os.path.join(norm_path, filename)
                dest_file = os.path.join(dest_dir, filename)

                print('process file: %s' % src_file)

                if not src_file.endswith('.less'):
                    if src_file.endswith('.css'):
                        shutil.copy(src_file, dest_file)
                        print('...copy')
                    print('...skeep')
                    continue

                print('...generate')

                dest_file = dest_file[:-5] + '.css'

                f = open(dest_file, 'w')
                (out, err) = subprocess.Popen(["lessc", src_file], stdout=f).communicate()
                f.close()

        print('all files processed')
