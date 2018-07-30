
import smart_imports

smart_imports.all()


class CodeTests(utils_testcase.TestCase):

    def setUp(self):
        super(CodeTests, self).setUp()

    def _filter_code(self, name, only_models=True):
        process = subprocess.Popen(['grep', '-R', name, django_settings.PROJECT_DIR], stdout=subprocess.PIPE)

        out, err = process.communicate()

        self.assertEqual(process.returncode, 0)

        out = [string for string in out.decode('utf-8').split('\n') if ':' in string]
        out = [string.split(':', 1) for string in out]
        out = [code
               for filename, code in out
               if ('migrations' not in filename and
                   'tests' not in filename and
                   '.pyc' not in filename and
                   '~' not in filename and
                   'code_tests.py' not in filename and
                   (not only_models or 'models.py' in filename) and
                   filename.endswith('.py'))]

        return out

    def test_every_foreign_key_has_on_delete_argument(self):
        for code in self._filter_code('ForeignKey'):
            self.assertTrue(' on_delete=' in code)

    def test_every_boolean_field_has_default_argument(self):
        for code in self._filter_code('BooleanField'):
            self.assertTrue('default=' in code)

    def check_starts(self, code, starts):
        return any(code.startswith(start) for start in starts)

    def test_only_absolute_imports__from(self):
        for code in self._filter_code('^\s*from ', only_models=False):
            code = code.strip()[len('from '):]
            self.assertTrue(self.check_starts(code,
                                              ['.',
                                               '..',
                                               'the_tale',
                                               'dext',
                                               'django',
                                               'rels',
                                               'optparse',
                                               'kombu',
                                               'decimal',
                                               'south',
                                               'questgen',
                                               'pynames',
                                               'deworld',
                                               'urlparse',
                                               'boto',
                                               'Queue',
                                               'utg',
                                               'functools',
                                               'urllib',
                                               'unittest',
                                               'tt_protocol',
                                               'tt_diary',
                                               'tt_logic']))

    def test_only_absolute_imports__import(self):

        for code in self._filter_code('^\s*import ', only_models=False):
            code = code.strip()[len('import '):]
            for module_name in code.split(','):
                module_name = module_name.strip()
                self.assertTrue(self.check_starts(module_name,
                                                  ['sys', 'os', 'shutil', 'datetime', 'tempfile', 'subprocess', 'random', 'collections', 're', 'itertools', 'Queue', 'time',
                                                   'jinja2', 'math', 'uuid', 'postmarkup', 'functools', 'urllib2', 'xlrd', 'copy', 'gv', 'string', 'traceback',
                                                   'markdown', 'md5', 'mock', 'pymorphy', 'numbers', 'gc', 'numpy', 'matplotlib', 'contextlib', 'pynames', 'json', 'PIL', 'deworld',
                                                   'urllib', 'socket', 'types', 'csv', 'getpass', 'logging', 'operator', 'hashlib', 'psutil', 'tt_protocol', 'tt_diary', 'queue',
                                                   'threading', 'site', 'tt_calendar', 'importlib', 'smart_imports']))

    def test_api_urls_not_changed(self):
        self.assertEqual(dext_urls.url('portal:api-info'), '/api/info')
        self.assertEqual(dext_urls.url('accounts:auth:api-login'), '/accounts/auth/api/login')
        self.assertEqual(dext_urls.url('accounts:auth:api-logout'), '/accounts/auth/api/logout')
        self.assertEqual(dext_urls.url('game:api-info'), '/game/api/info')
