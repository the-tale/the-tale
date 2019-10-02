
import smart_imports

smart_imports.all()


class Emissary(meta_relations_objects.MetaType):
    __slots__ = ('caption', )
    TYPE = 14
    TYPE_CAPTION = 'Эмиссар'

    def __init__(self, caption, **kwargs):
        super(Emissary, self).__init__(**kwargs)
        self.caption = caption

    @property
    def url(self):
        return dext_urls.url('game:emissaries:show', self.id)

    @classmethod
    def create_from_object(cls, emissary):
        return cls(id=emissary.id, caption=emissary.name)

    @classmethod
    def create_from_id(cls, id):
        emissary = logic.load_emissary(emissary_id=id)

        if emissary is None:
            return None

        return cls.create_from_object(emissary)

    @classmethod
    def create_from_ids(cls, ids):
        return [cls.create_from_id(id) for id in ids]
