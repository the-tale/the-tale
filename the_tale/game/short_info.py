# coding: utf-8

from the_tale.accounts import prototypes as accounts_prototypes
from the_tale.accounts.clans import prototypes as clans_prototypes

from the_tale.game.heroes import logic as heroes_logic

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

    for clan in clans_prototypes.ClanPrototype.get_list_by_id(list(clans_ids)):
        clan_info = ShortClanInfo(id=clan.id, abbr=clan.abbr, name=clan.name)
        for account in accounts.itervalues():
            if account.clan == clan.id:
                account.clan = clan_info

    return accounts
