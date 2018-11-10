
import smart_imports

smart_imports.all()


class Place(meta_relations_objects.MetaType):
    __slots__ = ('caption', )
    TYPE = 3
    TYPE_CAPTION = 'Город'

    def __init__(self, caption, **kwargs):
        super(Place, self).__init__(**kwargs)
        self.caption = caption

    @property
    def url(self):
        return dext_urls.url('game:places:show', self.id)

    @classmethod
    def create_from_object(cls, place):
        return cls(id=place.id, caption=place.name)

    @classmethod
    def create_from_id(cls, id):
        from . import storage

        place = storage.places.get(id)
        if place is None:
            return None

        return cls.create_from_object(place)

    @classmethod
    def create_from_ids(cls, ids):
        return [cls.create_from_id(id) for id in ids]
