# coding: utf-8

from dext.common.utils import jinja2

from the_tale.game.quests import logic


@jinja2.jinjaglobal
def choose_quest_path_url():
    return jinja2.Markup(logic.choose_quest_path_url())
