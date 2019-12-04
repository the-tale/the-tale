
import smart_imports

smart_imports.all()


@utils_jinja2.jinjaglobal
def has_broken_ingame_template():
    return prototypes.TemplatePrototype._db_filter(state=relations.TEMPLATE_STATE.IN_GAME).exclude(errors_status=relations.TEMPLATE_ERRORS_STATUS.NO_ERRORS).exists()
