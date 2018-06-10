
from dext.common.utils import jinja2

from . import storage
from . import logic


@jinja2.jinjaglobal
def all_places():
    return sorted(storage.places.all(), key=lambda p: p.name)


@jinja2.jinjaglobal
def hero_popularity(hero_id):
    return logic.get_hero_popularity(hero_id)
