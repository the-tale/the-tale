# coding: utf-8

from dext.jinja2.decorators import jinjaglobal

from the_tale.game.map.places.storage import places_storage

@jinjaglobal
def all_places():
    return sorted(places_storage.all(), key=lambda p: p.name)
