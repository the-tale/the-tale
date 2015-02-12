# coding: utf-8
import mock
import numpy as np
import matplotlib.pyplot as plt

from django.core.management.base import BaseCommand

from the_tale.accounts.prototypes import AccountPrototype
from the_tale.accounts.logic import register_user, remove_account

from the_tale.game.logic_storage import LogicStorage

from the_tale.game.actions import battle, contexts

from the_tale.game.balance.power import Power, PowerDistribution

from the_tale.game.heroes.habilities import ABILITIES, ABILITY_AVAILABILITY, ABILITY_TYPE


class Messanger(object):

    def add_message(self, *argv, **kwargs):
        pass


MESSANGER = Messanger()

TEST_BATTLES_NUMBER = 40
LEVEL = 5
HERO_LEVELS = [5, 15, 25, 35, 45]
POWER_DISTRIBUTION = PowerDistribution(0.5, 0.5)


def process_battle(hero_1, hero_2):

    hero_1_context = contexts.BattleContext()
    hero_2_context = contexts.BattleContext()

    while hero_1.health > 0 and hero_2.health > 0:
        battle.make_turn(battle.Actor(hero_1, hero_1_context),
                         battle.Actor(hero_2, hero_2_context ),
                         MESSANGER)

    return hero_1.health > 0

def get_battles_statistics(hero_1, hero_2):

    hero_1_wins = 0
    hero_2_wins = 0

    for hero_level in HERO_LEVELS:

        with mock.patch('the_tale.game.heroes.prototypes.HeroPrototype.power', Power.power_to_level(POWER_DISTRIBUTION, hero_level)):
            hero_1._model.level = hero_level
            hero_2._model.level = hero_level

            for i in xrange(TEST_BATTLES_NUMBER): # pylint: disable=W0612
                hero_1.health = hero_1.max_health
                hero_2.health = hero_2.max_health

                if process_battle(hero_1, hero_2):
                    hero_1_wins += 1
                else:
                    hero_2_wins += 1

    return hero_1_wins, hero_2_wins


def set_heroes_companion(hero_1, hero_2):
    from the_tale.game.companions import storage
    from the_tale.game.companions import models
    from the_tale.game.companions import logic

    COMPANION_NAME = u'test_hero_battle_companion'

    for companion in storage.companions.all():
        if companion.name.startswith(COMPANION_NAME):
            models.CompanionRecord.objects.filter(id=companion.id).delete()
            storage.companions.refresh()
            break

    companion_record = logic.create_random_companion_record(COMPANION_NAME)

    hero_1.set_companion(logic.create_companion(companion_record))
    hero_2.set_companion(logic.create_companion(companion_record))


def compare_abilities(hero_1, hero_2, abilities, level):

    hero_1.companion.health = hero_1.companion.max_health
    hero_2.companion.health = hero_2.companion.max_health

    ability_matches = {}

    for i, ability_1 in enumerate(abilities[:-1]):
        for ability_2 in abilities[i+1:]:

            hero_1.abilities.reset() #abilities = {}
            hero_1.abilities.add('hit', min(level, ABILITIES['hit'].MAX_LEVEL))
            hero_1.abilities.add(ability_1.get_id(), level)

            hero_2.abilities.reset() #abilities = {}
            hero_2.abilities.add('hit', min(level, ABILITIES['hit'].MAX_LEVEL))
            hero_2.abilities.add(ability_2.get_id(), level)

            hero_1_wins, hero_2_wins = get_battles_statistics(hero_1, hero_2)

            ability_matches[(ability_1.get_id(), ability_2.get_id())] = (hero_1_wins, hero_2_wins)

            print 'compared "%s" with "%s": %d/%d' % (ability_1.get_id(), ability_2.get_id(), hero_1_wins, hero_2_wins)

    return ability_matches


def save_ability_power_statistics(statistics):
    fig = plt.figure()
    ax = fig.add_subplot(111)

    x = np.arange(len(statistics))

    plt.bar(x, [s[1] for s in statistics], width=0.8, align='center')

    ax.set_xlim(-0.5, len(statistics)+0.5)
    ax.set_ylim(0, statistics[0][1])

    locator = plt.IndexLocator(1, 0.4)
    formatter = plt.FixedFormatter([s[0] for s in statistics])

    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(formatter)

    plt.setp(plt.getp(ax, 'xticklabels'), rotation=45, fontsize=8, horizontalalignment='right')

    ax.set_title('Wins per ability')

    plt.tight_layout()

    plt.savefig('/tmp/wins.png')


def save_ability_mathces_statistics(statistics, matches): # pylint: disable=R0914
    fig = plt.figure()
    ax = fig.add_subplot(111)

    keys, wins = zip(*statistics) # pylint: disable=W0612

    index = dict((key, i) for i, key in enumerate(keys))

    data = []
    for (x, y), (w_1, w_2) in matches.items():
        data.append((index[x], index[y], 1000 * w_1 / float(w_1+w_2) ))
        data.append((index[y], index[x], 1000 * w_2 / float(w_1+w_2) ))

    x, y, powers = zip(*data)

    ax.scatter(x, y, s=powers, marker='o', c=powers)

    ax.set_xlim(-0.5, len(statistics)+0.5)
    ax.set_ylim(-0.5, len(statistics)+0.5)

    locator = plt.IndexLocator(1, 0)
    formatter = plt.FixedFormatter([s[0] for s in statistics])

    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(formatter)
    plt.setp(plt.getp(ax, 'xticklabels'), rotation=45, fontsize=8, horizontalalignment='right')

    ax.yaxis.set_major_locator(locator)
    ax.yaxis.set_major_formatter(formatter)
    plt.setp(plt.getp(ax, 'yticklabels'), fontsize=8)

    ax.set_title('matches results')

    plt.tight_layout()

    plt.savefig('/tmp/matches.png')


def save_ability_wins_distribution(statistics, ability_wins):

    fig = plt.figure()
    ax = fig.add_subplot(111)

    keys, wins = zip(*statistics) # pylint: disable=W0612

    data = [ability_wins[key] for key in keys]
    ax.boxplot(data)#, positions=[i for i in xrange(len(keys))])

    ax.set_xlim(0.5, len(statistics)+0.5)
    ax.set_ylim(0, TEST_BATTLES_NUMBER*len(HERO_LEVELS))

    locator = plt.IndexLocator(1, 0.5)
    formatter = plt.FixedFormatter([s[0] for s in statistics])

    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(formatter)
    plt.setp(plt.getp(ax, 'xticklabels'), rotation=45, fontsize=8, horizontalalignment='right')

    ax.set_title('wins destribution')

    plt.tight_layout()

    plt.savefig('/tmp/wins_destribution.png')



class Command(BaseCommand):

    help = 'compare power of different abilities'

    def handle(self, *args, **options): # pylint: disable=R0914

        # account = AccountPrototype.get_by_nick('compare_abilities_user')
        # if account:
        #     account.remove()

        # account = AccountPrototype.get_by_nick('compare_abilities_user_2')
        # if account:
        #     account.remove()

        result, account_1_id, bundle_id = register_user('compare_abilities_user') # pylint: disable=W0612
        result, account_2_id, bundle_id = register_user('compare_abilities_user_2') # pylint: disable=W0612

        account_1 = AccountPrototype.get_by_id(account_1_id)
        account_2 = AccountPrototype.get_by_id(account_2_id)

        storage = LogicStorage()
        storage.load_account_data(account_1)
        storage.load_account_data(account_2)

        hero_1 = storage.accounts_to_heroes[account_1_id]
        hero_2 = storage.accounts_to_heroes[account_2_id]

        set_heroes_companion(hero_1, hero_2)

        try:

            abilities = [ability_class
                         for ability_class in ABILITIES.values()
                         if (ability_class.AVAILABILITY.value & ABILITY_AVAILABILITY.FOR_PLAYERS.value and
                             ability_class.get_id() != 'hit' and
                             ability_class.TYPE == ABILITY_TYPE.BATTLE) ]

            ability_matches = compare_abilities(hero_1, hero_2, abilities, level=LEVEL)

            ability_statistics = dict( (ability.get_id(), 0) for ability in abilities)
            ability_wins = dict( (ability.get_id(), []) for ability in abilities)

            for (ability_1_id, ability_2_id), (ability_1_wins, ability_2_wins) in ability_matches.items():
                ability_statistics[ability_1_id] = ability_statistics.get(ability_1_id, 0) + ability_1_wins
                ability_statistics[ability_2_id] = ability_statistics.get(ability_2_id, 0) + ability_2_wins

                ability_wins[ability_1_id].append(ability_1_wins)
                ability_wins[ability_2_id].append(ability_2_wins)

            statistics = sorted(ability_statistics.items(), key=lambda stat: -stat[1])

            battles_per_ability = TEST_BATTLES_NUMBER * (len(abilities)-1)

            for ability_id, wins in statistics:
                print '%d\t%.0f%%\t%s' % (wins, 100*float(wins)/(battles_per_ability*len(HERO_LEVELS)), ability_id)

            save_ability_power_statistics(statistics)
            save_ability_mathces_statistics(statistics, ability_matches)
            save_ability_wins_distribution(statistics, ability_wins)

        finally:
            remove_account(account_1)
            remove_account(account_2)
