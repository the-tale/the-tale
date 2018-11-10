
import smart_imports

smart_imports.all()


@dext_jinja2.jinjaglobal
def region_url(turn=None):
    return logic.region_url(turn=turn)
