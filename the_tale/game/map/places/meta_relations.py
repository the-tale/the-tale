# coding: utf-8

from dext.common.utils import urls

from the_tale.common.utils import meta_relations

from . import storage


class Place(meta_relations.MetaType):
    __slots__ = ('caption', )
    TYPE = 3
    TYPE_CAPTION = u'Город'

    def __init__(self, caption, **kwargs):
        super(Place, self).__init__(**kwargs)
        self.caption = caption

    @property
    def url(self):
        return urls.url('game:map:places:show', self.id)

    @classmethod
    def create_from_object(cls, place):
        return cls(id=place.id, caption=place.name)

    @classmethod
    def create_from_id(cls, id):
        place = storage.places_storage.get(id)
        if place is None:
            return None

        return cls.create_from_object(place)


    @classmethod
    def create_from_ids(cls, ids):
        return [cls.create_from_id(id) for id in ids]
