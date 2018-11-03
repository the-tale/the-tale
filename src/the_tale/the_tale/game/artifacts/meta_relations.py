
import smart_imports

smart_imports.all()


class Artifact(meta_relations_objects.MetaType):
    __slots__ = ('caption', )
    TYPE = 4
    TYPE_CAPTION = 'Артефакт'

    def __init__(self, caption, **kwargs):
        super(Artifact, self).__init__(**kwargs)
        self.caption = caption

    @property
    def url(self):
        return dext_urls.url('guide:artifacts:show', self.id)

    @classmethod
    def create_from_object(cls, artifact):
        return cls(id=artifact.id, caption=artifact.name)

    @classmethod
    def create_from_id(cls, id):
        from . import storage

        artifact = storage.artifacts.get(id)
        if artifact is None:
            return None

        return cls.create_from_object(artifact)

    @classmethod
    def create_from_ids(cls, ids):
        return [cls.create_from_id(id) for id in ids]
