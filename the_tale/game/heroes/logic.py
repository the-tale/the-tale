# -*- coding: utf-8 -*-
from .models import Hero
from .prototypes import get_hero_by_model
from . import game_info

def get_angel_heroes(angel_id):
    heroes = Hero.objects.filter(angel=angel_id)
    objects = [get_hero_by_model(hero) for hero in heroes]
    return objects

def strike(attaker, defender):
    result =  game_info.actions.battle.strike.do(attaker, defender)
    result.defender.health = result.defender.health - result.damage
    return result

def create_mob_for_hero(hero):
    from game.mobs.storage import MobsDatabase
    return MobsDatabase.storage().get_random_mob(hero)
