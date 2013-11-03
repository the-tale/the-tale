# coding: utf-8
import subprocess

from dext.utils.urls import url

from the_tale.common.utils import testcase


class CodeTests(testcase.TestCase):

    def setUp(self):
        super(CodeTests, self).setUp()


    def test_every_foreign_key_has_on_delete_argument(self):
        process = subprocess.Popen(['grep', '-R', 'ForeignKey', './the_tale'], stdout=subprocess.PIPE)

        out, err = process.communicate()

        self.assertEqual(process.returncode, 0)

        out = [string for string in out.split('\n') if ':' in string]
        out = [string.split(':', 1) for string in out]
        out = [code
               for filename, code in out
               if 'migrations' not in filename and '.pyc' not in filename and '~' not in filename and 'code_tests.py' not in filename]

        for code in out:
            self.assertTrue(' on_delete=' in code)

    def test_api_urls_not_changed(self):
        self.assertEqual(url('portal:api-info'), '/api/info')
        self.assertEqual(url('accounts:auth:api-login'), '/accounts/auth/api/login')
        self.assertEqual(url('accounts:auth:api-logout'), '/accounts/auth/api/logout')
        self.assertEqual(url('game:api-info'), '/game/api/info')
