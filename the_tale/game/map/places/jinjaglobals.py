# coding: utf-8

from dext.common.utils import jinja2

from the_tale.game.map.places.storage import places_storage

@jinja2.jinjaglobal
def all_places():
    return sorted(places_storage.all(), key=lambda p: p.name)
