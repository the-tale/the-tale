# -*- coding: utf-8 -*-
from dext.jinja2.decorators import jinjaglobal

from cms.models import Page
from cms.conf import cms_settings

SECTIONS_DICT = dict( (section.id, section) for section in cms_settings.SECTIONS)

@jinjaglobal
def get_cms_section_pages(section, *args, **kwargs):
    return Page.objects.filter(section=section, active=True).order_by('order')


@jinjaglobal
def get_cms_section_info(section):
    return SECTIONS_DICT[section]
