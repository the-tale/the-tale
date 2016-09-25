# coding: utf-8

from dext.common.utils import urls

from the_tale.common.utils import meta_relations

from . import storage


class Person(meta_relations.MetaType):
    __slots__ = ('caption', )
    TYPE = 10
    TYPE_CAPTION = u'Мастер'

    def __init__(self, caption, **kwargs):
        super(Person, self).__init__(**kwargs)
        self.caption = caption

    @property
    def url(self):
        return urls.url('game:persons:show', self.id)

    @classmethod
    def create_from_object(cls, person):
        return cls(id=person.id, caption=person.name)

    @classmethod
    def create_from_id(cls, id):
        person = storage.persons.get(id)

        if person is None:
            return None

        return cls.create_from_object(person)

    @classmethod
    def create_from_ids(cls, ids):
        return [cls.create_from_id(id) for id in ids]
