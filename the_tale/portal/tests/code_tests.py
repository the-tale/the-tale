# coding: utf-8
import subprocess

from django.conf import settings as project_settings
from django.utils.importlib import import_module

from dext.utils.urls import url

from the_tale.common.utils import testcase


class CodeTests(testcase.TestCase):

    def setUp(self):
        super(CodeTests, self).setUp()

    def _filter_code(self, name, only_models=True):
        process = subprocess.Popen(['grep', '-R', name, './the_tale'], stdout=subprocess.PIPE)

        out, err = process.communicate()

        self.assertEqual(process.returncode, 0)

        out = [string for string in out.split('\n') if ':' in string]
        out = [string.split(':', 1) for string in out]
        out = [code
               for filename, code in out
               if ('migrations' not in filename and
                   'tests' not in filename and
                   '.pyc' not in filename and
                   '~' not in filename and
                   'code_tests.py' not in filename and
                   (not only_models or 'models.py' in filename))]

        return out

    def test_every_foreign_key_has_on_delete_argument(self):
        for code in self._filter_code('ForeignKey'):
            self.assertTrue(' on_delete=' in code)


    def test_every_boolean_field_has_default_argument(self):
        for code in self._filter_code('BooleanField'):
            self.assertTrue('default=' in code)

    def test_api_urls_not_changed(self):
        self.assertEqual(url('portal:api-info'), '/api/info')
        self.assertEqual(url('accounts:auth:api-login'), '/accounts/auth/api/login')
        self.assertEqual(url('accounts:auth:api-logout'), '/accounts/auth/api/logout')
        self.assertEqual(url('game:api-info'), '/game/api/info')


    def test_storade_objects_got_only_from_storages(self):
        from the_tale.common.utils.storage import BaseStorage

        # get all stored types
        prototypes = []

        for app_path in project_settings.INSTALLED_APPS:
            storage_module = '%s.storage' % app_path
            try:
                module = import_module(storage_module)
            except:
                continue

            for object in module.__dict__.values():
                if isinstance(object, BaseStorage):
                    prototypes.append(object.PROTOTYPE)

        # check
        for prototype in prototypes:
            for code in self._filter_code(prototype.__name__, only_models=False):
                self.assertFalse(('%s.get_by' % prototype.__name__) in code)
                self.assertFalse(('%s.get_list_by' % prototype.__name__) in code)
                self.assertFalse(('%s._db_' % prototype.__name__) in code)
                self.assertFalse(('%s.from_query' % prototype.__name__) in code)
