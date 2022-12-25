
import smart_imports

smart_imports.all()


@utils_jinja2.jinjaglobal
def all_places():
    return sorted(storage.places.all(), key=lambda p: p.name)


@utils_jinja2.jinjaglobal
def hero_popularity(hero_id):
    return logic.get_hero_popularity(hero_id)


@utils_jinja2.jinjaglobal
def region_for_place(place_id):
    return places_storage.clans_regions.region_for_place(place_id)
