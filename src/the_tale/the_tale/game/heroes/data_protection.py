
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
    # code disabled due to moving the game into readonly mode
    # amqp_environment.environment.workers.supervisor.cmd_account_release_required(account_id)
    pass


def before_remove_data(account_id):
    account = accounts_prototypes.AccountPrototype.get_by_id(account_id)

    now = datetime.datetime.now()

    if account.removed_at is None:
        raise NotImplementedError('account MUST be marked for deletion')

    # TODO: potential bug, because we do not check bundles of heroes
    #       this is weak protection
    if now - account.removed_at < datetime.timedelta(seconds=conf.settings.REMOVE_HERO_DELAY):
        request_hero_release(account_id)
        return False

    hero = logic.load_hero(account_id)

    if hero.saved_at <= account.removed_at:
        request_hero_release(account_id)
        return False

    return True


def remove_data(account_id):

    hero = logic.load_hero(account_id)

    hero.set_utg_name(game_names.generator().get_name(hero.race, hero.gender))

    for preference in relations.PREFERENCE_TYPE.records:
        if preference.nullable:
            hero.preferences.set(preference, None)

    logic.sync_hero_external_data(hero)

    logic.save_hero(hero)

    logic.set_hero_description(hero_id=hero.id, text='')

    return True
