# coding: utf-8

import subprocess

from optparse import make_option

from django.core.management.base import BaseCommand
from django.conf import settings as project_settings

FABFILE = '/home/tie/repos/mine/devops/the_tale/deploy.py'

META_CONFIG = project_settings.META_CONFIG

class Command(BaseCommand):

    help = 'devops commands'

    requires_model_validation = False

    option_list = BaseCommand.option_list + ( make_option('-c', '--command',
                                                          action='store',
                                                          type=str,
                                                          dest='command',
                                                          help='command'),
                                            )

    def setup(self, host, user, newrelic):
        full_host = '%s@%s' % (user, host)
        subprocess.call(['fab', '-f', FABFILE, 'setup:static_data_version=%s,version=%s,domain=%s,host=%s,newrelic=%s' % (META_CONFIG.static_data_version,
                                                                                                                          META_CONFIG.version, # 'rc.0.2.6',
                                                                                                                          host,
                                                                                                                          full_host,
                                                                                                                          'true' if newrelic else 'false')])

    def handle(self, *args, **options):

        command = options['command']

        if command == 'setup':
            self.setup(host='the-tale.org', user='root', newrelic=True)
        if command == 'test-setup':
            self.setup(host='the-tale.com', user='root', newrelic=False)
        else:
            print 'unknown command'
