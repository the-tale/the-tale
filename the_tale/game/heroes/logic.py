# -*- coding: utf-8 -*-
from game.heroes.models import Hero
from game.heroes import game_info

def strike(attaker, defender):
    result =  game_info.actions.battle.strike.do(attaker, defender)
    result.defender.health = result.defender.health - result.damage
    return result

def create_mob_for_hero(hero):
    from game.mobs.storage import MobsDatabase
    return MobsDatabase.storage().get_random_mob(hero)
