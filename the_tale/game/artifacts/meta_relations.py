# coding: utf-8

from dext.common.utils import urls

from the_tale.common.utils import meta_relations

from . import storage


class Artifact(meta_relations.MetaType):
    __slots__ = ('caption', )
    TYPE = 4
    TYPE_CAPTION = u'Артефакт'

    def __init__(self, caption, **kwargs):
        super(Artifact, self).__init__(**kwargs)
        self.caption = caption

    @property
    def url(self):
        return urls.url('guide:artifacts:show', self.id)

    @classmethod
    def create_from_object(cls, artifact):
        return cls(id=artifact.id, caption=artifact.name)

    @classmethod
    def create_from_id(cls, id):
        artifact = storage.artifacts_storage.get(id)
        if artifact is None:
            return None

        return cls.create_from_object(artifact)


    @classmethod
    def create_from_ids(cls, ids):
        return [cls.create_from_id(id) for id in ids]
