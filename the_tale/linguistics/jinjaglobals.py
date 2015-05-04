# coding: utf-8

from dext.common.utils import jinja2

from the_tale.linguistics import prototypes
from the_tale.linguistics import relations


@jinja2.jinjaglobal
def has_broken_ingame_template():
    return prototypes.TemplatePrototype._db_filter(state=relations.TEMPLATE_STATE.IN_GAME).exclude(errors_status=relations.TEMPLATE_ERRORS_STATUS.NO_ERRORS).exists()
