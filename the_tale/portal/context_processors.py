# coding: utf-8

from portal.conf import SITE_SECTIONS


def section(request):
    section = None
    for regex, section_name in SITE_SECTIONS:
        if regex.match(request.path):
            section = section_name
            break
    return {'SECTION': section}
