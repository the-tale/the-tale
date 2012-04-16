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

def sell_in_city(seller, artifact, selling_crit):
    sell_price = game_info.actions.trading.trade_in_town.sell_price(seller, artifact, selling_crit)
    seller.money = seller.money + sell_price
    seller.bag.pop_artifact(artifact)
    return sell_price

def equip_in_city(hero):
    return game_info.actions.equipping.equip_in_town.equip(hero)


def create_mob_for_hero(hero):
    from ..mobs.storage import MobsStorage
    return MobsStorage.storage().get_random_mob(hero)
