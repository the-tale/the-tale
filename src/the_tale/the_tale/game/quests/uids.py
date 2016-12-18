# coding: utf-8

_UIDS_CACHE_PLACE = {}
_UIDS_CACHE_PERSON = {}
_UIDS_CACHE_HERO = {}
_UIDS_CACHE_MOB = {}


def place(place_id):
    if place_id not in _UIDS_CACHE_PLACE:
        _UIDS_CACHE_PLACE[place_id] = 'pl_%d' % place_id
    return _UIDS_CACHE_PLACE[place_id]

def person(person_id):
    if person_id not in _UIDS_CACHE_PERSON:
        _UIDS_CACHE_PERSON[person_id] = 'pe_%d' % person_id
    return _UIDS_CACHE_PERSON[person_id]

def hero(hero_id):
    if hero_id not in _UIDS_CACHE_HERO:
        _UIDS_CACHE_HERO[hero_id] = 'he_%d' % hero_id
    return _UIDS_CACHE_HERO[hero_id]

def mob(mob_id):
    if mob_id not in _UIDS_CACHE_MOB:
        _UIDS_CACHE_MOB[mob_id] = 'mo_%d' % mob_id
    return _UIDS_CACHE_MOB[mob_id]
