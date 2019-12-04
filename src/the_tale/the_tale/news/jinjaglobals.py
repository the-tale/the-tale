
import smart_imports

smart_imports.all()


@utils_jinja2.jinjaglobal
def get_last_news():
    try:
        return logic.load_last_news()
    except IndexError:
        return None
