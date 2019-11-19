
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
    def create_unknown(cls, id):
        return cls(id=id, caption='неизвестный эмиссар')

    @classmethod
    def create_from_id(cls, id):
        emissary = logic.load_emissary(emissary_id=id)

        if emissary is None:
            return cls.create_unknown(id)

        return cls.create_from_object(emissary)

    @classmethod
    def create_from_ids(cls, ids):
        return [cls.create_from_id(id) for id in ids]


class Event(meta_relations_objects.MetaType):
    __slots__ = ('caption', )
    TYPE = 15
    TYPE_CAPTION = 'Мероприятие эмиссара'

    def __init__(self, caption, **kwargs):
        super().__init__(**kwargs)
        self.caption = caption

    @property
    def url(self):
        return None

    @classmethod
    def create_from_object(cls, record):
        return cls(id=record.value, caption=record.text)

    @classmethod
    def create_from_id(cls, id):
        from . import relations
        return cls.create_from_object(relations.EVENT_TYPE(id))

    @classmethod
    def create_from_ids(cls, ids):
        return [cls.create_from_id(id) for id in ids]
