# coding: utf-8
import datetime

from dext.jinja2.decorators import jinjaglobal

from portal.newspaper.conf import newspaper_settings


@jinjaglobal
def get_edition_number():
    return (datetime.datetime.now() - newspaper_settings.FIRST_EDITION_DATE).days + 1
