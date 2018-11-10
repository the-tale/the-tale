
import smart_imports

smart_imports.all()


class Companion(meta_relations_objects.MetaType):
    __slots__ = ('caption', )
    TYPE = 6
    TYPE_CAPTION = 'Спутник'

    def __init__(self, caption, **kwargs):
        super(Companion, self).__init__(**kwargs)
        self.caption = caption

    @property
    def url(self):
        return dext_urls.url('guide:companions:show', self.id)

    @classmethod
    def create_from_object(cls, companion):
        return cls(id=companion.id, caption=companion.name)

    @classmethod
    def create_from_id(cls, id):
        from . import storage

        companion = storage.companions.get(id)
        if companion is None:
            return None

        return cls.create_from_object(companion)

    @classmethod
    def create_from_ids(cls, ids):
        return [cls.create_from_id(id) for id in ids]
