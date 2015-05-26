# coding: utf-8

from dext.common.meta_relations import objects as meta_relations_objects


class MetaType(meta_relations_objects.MetaType):
    __slots__ = ()
    TYPE_CAPTION = NotImplemented

    def __init__(self, **kwargs):
        super(MetaType, self).__init__(**kwargs)

    caption = NotImplemented
    url = NotImplemented


class MetaRelation(meta_relations_objects.MetaRelation):
    pass
