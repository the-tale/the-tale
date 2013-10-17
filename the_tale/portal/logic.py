# coding: utf-8

from django.conf import settings as project_settings

from dext.settings import settings
from dext.utils import s11n

from portal.conf import portal_settings

from common.utils import cdn


def cdn_paths():

    if project_settings.CDNS_ENABLED and portal_settings.SETTINGS_CDN_INFO_KEY in settings:
        return s11n.from_json(settings[portal_settings.SETTINGS_CDN_INFO_KEY])

    return cdn.get_local_paths(project_settings.CDNS)
