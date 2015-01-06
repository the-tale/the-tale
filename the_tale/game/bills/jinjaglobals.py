# coding: utf-8

from dext.jinja2.decorators import jinjaglobal

from the_tale.game.bills.bills import BILLS_BY_ID


@jinjaglobal
def bills_menu_types():
    return sorted(BILLS_BY_ID.items(), key=lambda x: x[1].type.text)
