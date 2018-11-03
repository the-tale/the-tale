
import smart_imports

smart_imports.all()


class Person(meta_relations_objects.MetaType):
    __slots__ = ('caption', )
    TYPE = 10
    TYPE_CAPTION = 'Мастер'

    def __init__(self, caption, **kwargs):
        super(Person, self).__init__(**kwargs)
        self.caption = caption

    @property
    def url(self):
        return dext_urls.url('game:persons:show', self.id)

    @classmethod
    def create_from_object(cls, person):
        return cls(id=person.id, caption=person.name)

    @classmethod
    def create_from_id(cls, id):
        from . import storage
        person = storage.persons.get(id)

        if person is None:
            return None

        return cls.create_from_object(person)

    @classmethod
    def create_from_ids(cls, ids):
        return [cls.create_from_id(id) for id in ids]
