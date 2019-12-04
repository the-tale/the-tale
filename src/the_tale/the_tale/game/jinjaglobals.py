
import smart_imports

smart_imports.all()


@utils_jinja2.jinjaglobal
def game_info_url(account=None, client_turns=None):
    return utils_jinja2.Markup(logic.game_info_url(account_id=account.id if account is not None else None,
                                                  client_turns=client_turns))


@utils_jinja2.jinjaglobal
def game_diary_url():
    return utils_jinja2.Markup(logic.game_diary_url())


@utils_jinja2.jinjaglobal
def game_names_url():
    return utils_jinja2.Markup(logic.game_names_url())


@utils_jinja2.jinjaglobal
def game_hero_history_url():
    return utils_jinja2.Markup(logic.game_hero_history_url())


@utils_jinja2.jinjafilter
def verbose_game_date(turn_number):
    return game_turn.game_datetime(turn_number).date.verbose_full()


@utils_jinja2.jinjaglobal
def game_datetime(turn_number=None):
    return game_turn.game_datetime(turn_number)


@utils_jinja2.jinjaglobal
def communication_abilities(mob):
    levels = []

    if mob.communication_verbal.is_CAN:
        levels.append('вербальная')

    if mob.communication_gestures.is_CAN:
        levels.append('невербальная')

    if mob.communication_telepathic.is_CAN:
        levels.append('телепатия')

    if not levels:
        levels.append('—')

    return ', '.join(levels)
