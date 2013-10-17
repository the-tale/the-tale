# coding: utf-8

from dext.jinja2.decorators import jinjaglobal

from game import logic


@jinjaglobal
def game_info_url(account=None):
    return logic.game_info_url(account_id=account.id if account is not None else None)
