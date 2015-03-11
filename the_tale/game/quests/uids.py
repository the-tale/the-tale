# coding: utf-8

_UIDS_CACHE_PLACE = {}
_UIDS_CACHE_PERSON = {}
_UIDS_CACHE_HERO = {}
_UIDS_CACHE_MOB = {}


def place(place):
    if place.id not in _UIDS_CACHE_PLACE:
        _UIDS_CACHE_PLACE[place.id] = 'pl_%d' % place.id
    return _UIDS_CACHE_PLACE[place.id]

def person(person):
    if person.id not in _UIDS_CACHE_PERSON:
        _UIDS_CACHE_PERSON[person.id] = 'pe_%d' % person.id
    return _UIDS_CACHE_PERSON[person.id]

def hero(hero):
    if hero.id not in _UIDS_CACHE_HERO:
        _UIDS_CACHE_HERO[hero.id] = 'he_%d' % hero.id
    return _UIDS_CACHE_HERO[hero.id]

def mob(mob):
    if mob.id not in _UIDS_CACHE_MOB:
        _UIDS_CACHE_MOB[mob.id] = 'mo_%d' % mob.id
    return _UIDS_CACHE_MOB[mob.id]
