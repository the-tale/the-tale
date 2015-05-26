# coding: utf-8

from dext.common.utils import urls

from the_tale.common.utils import meta_relations

from . import prototypes


class Clan(meta_relations.MetaType):
    __slots__ = ('caption', )
    TYPE = 8
    TYPE_CAPTION = u'Гильдия'

    def __init__(self, caption, **kwargs):
        super(Clan, self).__init__(**kwargs)
        self.caption = caption

    @property
    def url(self):
        return urls.url('accounts:clans:show', self.id)

    @classmethod
    def create_from_object(cls, clan):
        return cls(id=clan.id, caption=clan.name)

    @classmethod
    def create_from_id(cls, id):
        clan = prototypes.ClanPrototype.get_by_id(id)
        if clan is None:
            return None

        return cls.create_from_object(clan)

    @classmethod
    def create_from_ids(cls, ids):
        return [cls.create_from_id(id) for id in ids]
