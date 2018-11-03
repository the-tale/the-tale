
import smart_imports

smart_imports.all()


class ShortHeroInfo(object):
    __slots__ = ('name', 'race', 'gender', 'level')

    def __init__(self, name, race, gender, level):
        self.name = name
        self.race = race
        self.gender = gender
        self.level = level


class ShortClanInfo(object):
    __slots__ = ('id', 'abbr', 'name')

    def __init__(self, id, abbr, name):
        self.id = id
        self.abbr = abbr
        self.name = name


class ShortAccountInfo(object):
    __slots__ = ('id', 'name', 'hero', 'clan')

    def __init__(self, id, name, hero, clan):
        self.id = id
        self.name = name
        self.hero = hero
        self.clan = clan

    @property
    def nick_verbose(self):
        if self.name.startswith(accounts_conf.settings.RESET_NICK_PREFIX):
            return accounts_conf.settings.RESET_NICK_PREFIX

        return self.name


def get_accounts_accounts_info(accounts_ids):
    heroes = {}

    for hero in heroes_logic.load_heroes_by_account_ids(accounts_ids):
        heroes[hero.id] = ShortHeroInfo(name=hero.name, race=hero.race, gender=hero.gender, level=hero.level)

    clans_ids = set()

    accounts = {}
    for account in accounts_prototypes.AccountPrototype.get_list_by_id(accounts_ids):
        if account.clan_id is not None:
            clans_ids.add(account.clan_id)
        accounts[account.id] = ShortAccountInfo(id=account.id, name=account.nick, hero=heroes[account.id], clan=account.clan_id)

    for clan in clans_logic.load_clans(list(clans_ids)):
        clan_info = ShortClanInfo(id=clan.id, abbr=clan.abbr, name=clan.name)
        for account in accounts.values():
            if account.clan == clan.id:
                account.clan = clan_info

    return accounts
