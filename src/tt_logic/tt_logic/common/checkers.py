
import datetime

from . import constants


def is_player_participate_in_game(is_banned, active_end_at, is_premium):
    if is_banned:
        return False

    now = datetime.datetime.now()

    if now < active_end_at:
        return True

    if is_premium and ((now - active_end_at).total_seconds() < constants.INACTIVE_PREMIUM_LIVETIME):
        return True

    return False
