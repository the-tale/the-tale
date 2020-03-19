
import smart_imports

smart_imports.all()


class Command(utilities_base.Command):

    help = 'run tests for all non-django applications'

    LOCKS = []

    requires_model_validation = False

    def _handle(self, *args, **options):
        subprocess.call("rm -f `find ./ -name '*.pyc'`", shell=True)

        tests = []
        for application in django_apps.apps.get_app_configs():
            label = application.name.split('.')

            if label[0] == 'django':
                continue

            tests_path = '%s.tests' % application.name
            if discovering.is_module_exists(tests_path):
                tests.append(tests_path)

        result = logic.run_django_command(['test', '--nomigrations'] + tests)

        print('test result: ', result)
