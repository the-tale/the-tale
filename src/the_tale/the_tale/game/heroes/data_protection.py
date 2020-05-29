
import smart_imports

smart_imports.all()


def collect_data(account_id):
    data = []

    hero = logic.load_hero(account_id)

    data.append(('hero:short_name', hero.name))
    data.append(('hero:long_name', hero.utg_name.serialize()))
    data.append(('hero:description', logic.get_hero_description(hero.id)))

    return data


def request_hero_release(account_id):
    amqp_environment.environment.workers.supervisor.cmd_account_release_required(account_id)


def remove_data(account_id):
    account = accounts_prototypes.AccountPrototype.get_by_id(account_id)

    now = datetime.datetime.now()

    if account.removed_at is None:
        raise NotImplementedError('account MUST be marked for deletion')

    if now - account.removed_at < datetime.timedelta(seconds=conf.settings.REMOVE_HERO_DELAY):
        request_hero_release(account_id)
        return False

    hero = logic.load_hero(account_id)

    if hero.saved_at <= account.removed_at:
        request_hero_release(account_id)
        return False

    hero.set_utg_name(game_names.generator().get_name(hero.race, hero.gender))

    for preference in relations.PREFERENCE_TYPE.records:
        if preference.nullable:
            hero.preferences.set(preference, None)

    zero = datetime.datetime.fromtimestamp(0)

    hero.update_with_account_data(is_fast=hero.is_fast,
                                  premium_end_at=zero,
                                  active_end_at=zero,
                                  ban_end_at=zero,
                                  might=0,
                                  actual_bills=[],
                                  clan_id=None)

    logic.save_hero(hero)

    logic.set_hero_description(hero_id=hero.id, text='')

    return True
