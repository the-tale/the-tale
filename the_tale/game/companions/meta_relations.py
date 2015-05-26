# coding: utf-8

from dext.common.utils import urls

from the_tale.common.utils import meta_relations

from . import storage


class Companion(meta_relations.MetaType):
    __slots__ = ('caption', )
    TYPE = 6
    TYPE_CAPTION = u'Спутник'

    def __init__(self, caption, **kwargs):
        super(Companion, self).__init__(**kwargs)
        self.caption = caption

    @property
    def url(self):
        return urls.url('guide:companions:show', self.id)

    @classmethod
    def create_from_object(cls, companion):
        return cls(id=companion.id, caption=companion.name)

    @classmethod
    def create_from_id(cls, id):
        companion = storage.companions.get(id)
        if companion is None:
            return None

        return cls.create_from_object(companion)

    @classmethod
    def create_from_ids(cls, ids):
        return [cls.create_from_id(id) for id in ids]
