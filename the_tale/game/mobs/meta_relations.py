# coding: utf-8

from dext.common.utils import urls

from the_tale.common.utils import meta_relations

from . import storage


class Mob(meta_relations.MetaType):
    __slots__ = ('caption', )
    TYPE = 5
    TYPE_CAPTION = u'Монстр'

    def __init__(self, caption, **kwargs):
        super(Mob, self).__init__(**kwargs)
        self.caption = caption

    @property
    def url(self):
        return urls.url('guide:mobs:show', self.id)

    @classmethod
    def create_from_object(cls, mob):
        return cls(id=mob.id, caption=mob.name)

    @classmethod
    def create_from_id(cls, id):
        mob = storage.mobs_storage.get(id)
        if mob is None:
            return None

        return cls.create_from_object(mob)


    @classmethod
    def create_from_ids(cls, ids):
        return [cls.create_from_id(id) for id in ids]
