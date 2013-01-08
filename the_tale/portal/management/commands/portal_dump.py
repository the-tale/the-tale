# coding: utf-8
import os
import shutil
import datetime
import tempfile
import subprocess

from django.core.management.base import BaseCommand
from django.conf import settings as project_settings
from django.core.mail import EmailMessage

from portal.conf import portal_settings

class Command(BaseCommand):

    help = 'dump all dymamic portal data and send to email from settings.DUMP_EMAIL'

    requires_model_validation = False

    def handle(self, *args, **options):

        tmp_dir = tempfile.mkdtemp()

        try:
            timestamp_string = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')

            backup_dir = os.path.join(tmp_dir, timestamp_string)

            os.mkdir(backup_dir)

            for db_name, db_data in project_settings.DATABASES.items():
                backup_file_name = os.path.join(backup_dir, db_data['NAME'] + '.sql')
                print 'dump: %s' % db_name
                cmd = 'pg_dump -U "%(db_user)s" "%(db_name)s" > "%(file_name)s"' % {'db_user': db_data['USER'],
                                                                                    'db_name': db_data['NAME'],
                                                                                    'file_name': backup_file_name}
                subprocess.call(cmd, shell=True)

            print 'make archive'

            raw_archive_path = os.path.join(tmp_dir, timestamp_string)

            archive_file = shutil.make_archive(raw_archive_path,
                                               format='gztar',
                                               root_dir=tmp_dir,
                                               base_dir=timestamp_string)

            print 'archive created: %s' % archive_file

            shutil.copyfile(archive_file, '/home/the-tale/last_backup.gztar')

            # print 'send email to %s' % portal_settings.DUMP_EMAIL

            # email = EmailMessage('[BACKUP][the-tale.org] %s' % timestamp_string,
            #                      'backup file for %s' % timestamp_string,
            #                      'no-reply@the-tale.org',
            #                      [portal_settings.DUMP_EMAIL])
            # email.attach_file(archive_file)
            # email.send()

        except:
            raise
        finally:
            shutil.rmtree(tmp_dir)
