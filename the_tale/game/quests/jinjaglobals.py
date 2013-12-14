# coding: utf-8

import jinja2

from dext.jinja2.decorators import jinjaglobal

from the_tale.game.quests import logic


@jinjaglobal
def choose_quest_path_url():
    return jinja2.Markup(logic.choose_quest_path_url())
