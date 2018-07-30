
import smart_imports

smart_imports.all()


@dext_jinja2.jinjaglobal
def use_ability_url(ability, building=None, battle=None):
    return jinja2.Markup(logic.use_ability_url(ability=ability, building=building, battle=battle))
