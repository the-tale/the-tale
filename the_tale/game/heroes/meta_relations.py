# coding: utf-8

from dext.common.utils import urls

from the_tale.common.utils import meta_relations


class Hero(meta_relations.MetaType):
    __slots__ = ('caption', )
    TYPE = 9
    TYPE_CAPTION = u'Герой'

    def __init__(self, caption, **kwargs):
        super(Hero, self).__init__(**kwargs)
        self.caption = caption

    @property
    def url(self):
        return urls.url('game:heroes:show', self.id)

    @classmethod
    def create_from_object(cls, hero):
        return cls(id=hero.id, caption=hero.name)

    @classmethod
    def create_from_id(cls, id):
        hero = prototypes.HeroPrototype.get_by_id(id)
        if hero is None:
            return None

        return cls.create_from_object(hero)

    @classmethod
    def create_from_ids(cls, ids):
        return [cls.create_from_id(id) for id in ids]
