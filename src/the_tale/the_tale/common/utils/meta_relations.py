
import smart_imports

smart_imports.all()


class MetaType(dext_meta_relations_objects.MetaType):
    __slots__ = ()
    TYPE_CAPTION = NotImplemented

    def __init__(self, **kwargs):
        super(MetaType, self).__init__(**kwargs)

    caption = NotImplemented
    url = NotImplemented


class MetaRelation(dext_meta_relations_objects.MetaRelation):
    pass
