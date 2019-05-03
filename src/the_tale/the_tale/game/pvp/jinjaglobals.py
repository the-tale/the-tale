
import smart_imports

smart_imports.all()


@dext_jinja2.jinjaglobal
def pvp_page_url():
    return dext_jinja2.Markup(logic.pvp_page_url())


@dext_jinja2.jinjaglobal
def pvp_info_url():
    return dext_jinja2.Markup(logic.pvp_info_url())


@dext_jinja2.jinjaglobal
def pvp_call_to_arena_url():
    return dext_jinja2.Markup(logic.pvp_call_to_arena_url())


@dext_jinja2.jinjaglobal
def pvp_leave_arena_url():
    return dext_jinja2.Markup(logic.pvp_leave_arena_url())


@dext_jinja2.jinjaglobal
def pvp_accept_arena_battle_url():
    return dext_jinja2.Markup(logic.pvp_accept_arena_battle_url())


@dext_jinja2.jinjaglobal
def pvp_create_arena_bot_battle_url():
    return dext_jinja2.Markup(logic.pvp_create_arena_bot_battle_url())
