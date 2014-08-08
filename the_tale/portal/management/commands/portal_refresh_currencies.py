# coding: utf-8

from django.core.management.base import BaseCommand
from django.conf import settings as project_settings

from dext.settings import settings
from dext.common.utils import s11n

from the_tale.common.utils import currencies

from the_tale.portal.conf import portal_settings


class Command(BaseCommand):

    help = 'refresh currencies info'

    def handle(self, *args, **options):

        info = currencies.get_currencies_info(project_settings.CURRENCIES_BASE, project_settings.CURRENCIES_LIST)

        settings[portal_settings.SETTINGS_CURRENCIES_INFO_KEY] = s11n.to_json(info)
