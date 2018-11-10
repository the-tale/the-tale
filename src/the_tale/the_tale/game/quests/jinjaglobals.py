
import smart_imports

smart_imports.all()


@dext_jinja2.jinjaglobal
def choose_quest_path_url():
    return jinja2.Markup(logic.choose_quest_path_url())
