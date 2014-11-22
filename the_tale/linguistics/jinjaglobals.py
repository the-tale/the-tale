# coding: utf-8

from dext.jinja2.decorators import jinjaglobal

from the_tale.linguistics import prototypes
from the_tale.linguistics import relations


@jinjaglobal
def has_broken_ingame_template():
    return prototypes.TemplatePrototype._db_filter(state=relations.TEMPLATE_STATE.IN_GAME).exclude(errors_status=relations.TEMPLATE_ERRORS_STATUS.NO_ERRORS).exists()
