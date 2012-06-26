# -*- coding: utf-8 -*-

def create_mob_for_hero(hero):
    from game.mobs.storage import MobsDatabase
    return MobsDatabase.storage().get_random_mob(hero)
