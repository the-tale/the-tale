# coding: utf-8

from dext.common.utils import jinja2
from the_tale.game.bills.bills import BILLS_BY_ID


@jinja2.jinjaglobal
def bills_menu_types():
    return sorted(BILLS_BY_ID.items(), key=lambda x: x[1].type.text)
