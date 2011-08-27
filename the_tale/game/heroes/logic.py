# -*- coding: utf-8 -*-
import random
from .models import Hero
from .prototypes import get_hero_by_model, HeroPrototype

from . import game_info

def get_angel_heroes(angel_id):
    heroes = Hero.objects.filter(angel=angel_id)
    objects = [get_hero_by_model(hero) for hero in heroes]
    return objects

def strike(attaker, defender):
    result =  game_info.actions.battle.strike.do(attaker, defender)
    result.defender.health = result.defender.health - result.damage
    return result

def heal_in_town(pacient):
    heal_amount = game_info.actions.healing.heal_in_town.amount(pacient)
    pacient.health = min(pacient.max_health, pacient.health + heal_amount)
    return heal_amount

def sell_in_city(seller, artifact_uuid, selling_crit):
    sell_price = game_info.actions.trading.trade_in_town.sell_price(seller, artifact_uuid, selling_crit)
    seller.money = seller.money + sell_price
    seller.bag.pop_artifact(artifact_uuid)
    return sell_price

def equip_in_city(hero):
    return game_info.actions.equipping.equip_in_town.equip(hero)


def create_npc_for_hero(hero):
    npc = HeroPrototype.create(angel=None, 
                               name='NPC', 
                               first=False, 
                               intellect=random.randint(1, max(1, hero.intellect-1) ),
                               constitution=random.randint(1, max(1, hero.constitution-1) ),
                               reflexes=random.randint(1, max(1, hero.reflexes-1) ),
                               charisma=random.randint(1, max(1, hero.charisma-1) ), 
                               chaoticity=random.randint(1, max(1, hero.chaoticity-1) ), 
                               npc=True)
    return npc


def next_turn_pre_update_heroes(cur_turn, next_turn):
    for hero_model in Hero.objects.all():
        hero = get_hero_by_model(hero_model)

        hero.next_turn_pre_update(next_turn)
        hero.save()
    

def next_turn_post_update_heroes(cur_turn, next_turn):
    
    for hero_model in Hero.objects.all():
        hero = get_hero_by_model(hero_model)

        if hero.is_npc and not hero.is_alive and len(hero.get_actions()) == 1:
            hero.actions[0].remove()
            hero.remove()
            return

        hero.next_turn_post_update(next_turn)
        hero.save()
