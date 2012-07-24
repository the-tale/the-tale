# -*- coding: utf-8 -*-
from dext.jinja2.decorators import jinjaglobal

from cms.models import Page

@jinjaglobal
def get_cms_section_pages(section, *args, **kwargs):
    return Page.objects.filter(section=section, active=True).order_by('order')
