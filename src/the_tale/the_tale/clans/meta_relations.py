
import smart_imports

smart_imports.all()


class Clan(meta_relations_objects.MetaType):
    __slots__ = ('caption', )
    TYPE = 8
    TYPE_CAPTION = 'Гильдия'

    def __init__(self, caption, **kwargs):
        super().__init__(**kwargs)
        self.caption = caption

    @property
    def url(self):
        return dext_urls.url('clans:show', self.id)

    @classmethod
    def create_from_object(cls, clan):
        return cls(id=clan.id, caption=clan.name)

    @classmethod
    def create_removed(cls):
        return cls(id=None, caption='неизвестная гильдия')

    @classmethod
    def create_from_id(cls, id):
        clan = logic.load_clan(clan_id=id)

        if clan is None:
            return cls.create_removed()

        return cls.create_from_object(clan)

    @classmethod
    def create_from_ids(cls, ids):
        records = models.Clan.objects.filter(id__in=ids)

        if len(ids) != len(records):
            raise meta_relations_exceptions.ObjectsNotFound(type=cls.TYPE, ids=ids)

        return [cls.create_from_object(logic.load_clan(clan_model=record)) for record in records]


class Event(meta_relations_objects.MetaType):
    __slots__ = ('caption', )
    TYPE = 13
    TYPE_CAPTION = 'Событие гильдии'

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
        return cls.create_from_object(relations.EVENT(id))

    @classmethod
    def create_from_ids(cls, ids):
        return [cls.create_from_id(id) for id in ids]
