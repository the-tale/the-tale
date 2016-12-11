# coding: utf-8

from the_tale.portal.conf import SITE_SECTIONS
from the_tale.portal import logic


def section(request):
    section_ = None
    for regex, section_name in SITE_SECTIONS:
        if regex.match(request.path):
            section_ = section_name
            break
    return {'SECTION': section_}


def cdn_paths(request):
    return logic.cdn_paths()
