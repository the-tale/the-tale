# coding: utf-8
import os
import shutil
import datetime
import tempfile
import subprocess

from django.core.management.base import BaseCommand
from django.conf import settings as project_settings
# from django.core.mail import EmailMessage

from the_tale.portal.conf import portal_settings


def send_to_s3(backupname, filename):
    from boto.s3.connection import S3Connection
    from boto.s3.key import Key

    print 'send to Amazon S3'

    print 'create connection'

    conn = S3Connection(portal_settings.AWS_ACCESS_KEY, portal_settings.AWS_SECRET_KEY)

    print 'get bucket'
    backups = conn.get_bucket(portal_settings.AWS_S3_BACKUP_BUCKET)

    print 'create key'
    k = Key(backups)

    k.key = backupname

    print 'upload file'

    k.set_contents_from_filename(filename)



class Command(BaseCommand):

    help = 'dump all dymamic portal data and send to email from settings.DUMP_EMAIL'


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

            shutil.copyfile(archive_file, portal_settings.LAST_BACKUP_PATH)

            send_to_s3(timestamp_string, archive_file)

            # print 'send email to %s' % portal_settings.DUMP_EMAIL

            # email = EmailMessage('[BACKUP][%s] %s' % (project_settings.SITE_URL, timestamp_string ),
            #                      'backup file for %s' % timestamp_string,
            #                      project_settings.SERVER_EMAIL,
            #                      [portal_settings.DUMP_EMAIL])
            # email.attach_file(archive_file)
            # email.send()

        except:
            raise
        finally:
            shutil.rmtree(tmp_dir)
