# coding: utf-8
import mock
import numpy as np
import matplotlib.pyplot as plt

from django.core.management.base import BaseCommand

from accounts.prototypes import AccountPrototype
from accounts.logic import register_user, remove_account

from game.logic_storage import LogicStorage

from game.actions import battle, contexts

from game.balance import formulas as f

from game.heroes.habilities import ABILITIES, ABILITY_AVAILABILITY, ABILITY_TYPE


class Messanger(object):

    def add_message(self, *argv, **kwargs):
        pass

MESSANGER = Messanger()

TEST_BATTLES_NUMBER = 40
LEVEL = 5
HERO_LEVELS = [5, 15, 25, 35, 45]


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

        with mock.patch('game.heroes.prototypes.HeroPrototype.power', f.power_to_lvl(hero_level)):

            hero_1.model.level = hero_level
            hero_2.model.level = hero_level

            for i in xrange(TEST_BATTLES_NUMBER):
                hero_1.health = hero_1.max_health
                hero_2.health = hero_2.max_health

                if process_battle(hero_1, hero_2):
                    hero_1_wins += 1
                else:
                    hero_2_wins += 1

    return hero_1_wins, hero_2_wins


def compare_abilities(hero_1, hero_2, abilities, level):

    ability_matches = {}

    for i, ability_1 in enumerate(abilities[:-1]):
        for ability_2 in abilities[i+1:]:

            hero_1.abilities.abilities = {}
            hero_1.abilities.add('hit', level)
            hero_1.abilities.add(ability_1.get_id(), level)

            hero_2.abilities.abilities = {}
            hero_2.abilities.add('hit', level)
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


def save_ability_mathces_statistics(statistics, matches):
    fig = plt.figure()
    ax = fig.add_subplot(111)

    keys, wins = zip(*statistics)

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

    keys, wins = zip(*statistics)

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

    def handle(self, *args, **options):

        result, account_1_id, bundle_id = register_user('test_user')
        result, account_2_id, bundle_id = register_user('test_user_2')

        account_1 = AccountPrototype.get_by_id(account_1_id)
        account_2 = AccountPrototype.get_by_id(account_2_id)

        storage = LogicStorage()
        storage.load_account_data(account_1)
        storage.load_account_data(account_2)

        hero_1 = storage.accounts_to_heroes[account_1_id]
        hero_2 = storage.accounts_to_heroes[account_2_id]

        try:

            abilities = [ability_class
                         for ability_class in ABILITIES.values()
                         if (ability_class.AVAILABILITY & ABILITY_AVAILABILITY.FOR_PLAYERS and
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
