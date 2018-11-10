
import smart_imports

smart_imports.all()


class Mob(meta_relations_objects.MetaType):
    __slots__ = ('caption', )
    TYPE = 5
    TYPE_CAPTION = 'Монстр'

    def __init__(self, caption, **kwargs):
        super(Mob, self).__init__(**kwargs)
        self.caption = caption

    @property
    def url(self):
        return dext_urls.url('guide:mobs:show', self.id)

    @classmethod
    def create_from_object(cls, mob):
        return cls(id=mob.id, caption=mob.name)

    @classmethod
    def create_from_id(cls, id):
        from . import storage

        mob = storage.mobs.get(id)
        if mob is None:
            return None

        return cls.create_from_object(mob)

    @classmethod
    def create_from_ids(cls, ids):
        return [cls.create_from_id(id) for id in ids]
