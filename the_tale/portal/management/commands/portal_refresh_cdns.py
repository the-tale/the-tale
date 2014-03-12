# coding: utf-8

from django.core.management.base import BaseCommand
from django.conf import settings as project_settings

from dext.settings import settings
from dext.utils import s11n

from the_tale.common.utils import cdn

from the_tale.portal.conf import portal_settings


class Command(BaseCommand):

    help = 'refresh CDNs info'

    def handle(self, *args, **options):

        print 'refresh CDNs'

        info = cdn.get_cdns_info(project_settings.CDNS)

        settings[portal_settings.SETTINGS_CDN_INFO_KEY] = s11n.to_json(info)
