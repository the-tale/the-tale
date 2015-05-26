# coding: utf-8

from dext.common.utils import urls

from the_tale.common.utils import meta_relations
from the_tale.common.utils.decorators import lazy_property

from . import prototypes


class Post(meta_relations.MetaType):
    __slots__ = ('caption', '_object__lazy')
    TYPE = 1
    TYPE_CAPTION = u'Произведение'

    def __init__(self, caption, **kwargs):
        super(Post, self).__init__(**kwargs)
        self.caption = caption
        self._object__lazy = None

    @property
    def url(self):
        return urls.url('blogs:posts:show', self.id)

    @classmethod
    def create_from_object(cls, post):
        object = cls(id=post.id, caption=post.caption)
        object._object__lazy = post
        return object

    @lazy_property
    def object(self):
        return prototypes.PostPrototype.get_by_id(self.id)

    @classmethod
    def create_from_id(cls, id):
        post = prototypes.PostPrototype.get_by_id(id)
        if post is None:
            return None
        return cls.create_from_object(post)

    @classmethod
    def create_from_ids(cls, ids):
        return [cls(id=id, caption=caption) for id, caption in prototypes.PostPrototype._db_filer(ids__in=ids).values_list('id', 'caption')]


class IsAbout(meta_relations.MetaRelation):
    TYPE = 1
