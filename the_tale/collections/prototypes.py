# coding: utf-8

from common.utils.prototypes import BasePrototype
from common.utils.decorators import lazy_property
from common.utils import bbcode

from achievements.models import Collection, Kit, Item


class CollectionPrototype(BasePrototype):
    _model_class = Collection
    _readonly = ('id', 'created_at', 'updated_at', 'CAPTION_MAX_LENGTH', 'DESCRIPTION_MAX_LENGTH')
    _bidirectional = ('caption', 'description', 'approved', )
    _get_by = ('id', )

    @classmethod
    def approved_collections(cls):
        return cls.from_query(cls._db_filter(approved=True))

    @classmethod
    def all_collections(cls):
        return cls._db_all()

    @property
    def description_html(self): return bbcode.render(self.description)

    @classmethod
    def create(cls, caption, description, approved=False):
        model = cls._model_class.objects.create(caption=caption,
                                                description=description,
                                                approved=approved)

        return cls(model=model)


class KitPrototype(BasePrototype):
    _model_class = Kit
    _readonly = ('id', 'created_at', 'updated_at', 'CAPTION_MAX_LENGTH', 'DESCRIPTION_MAX_LENGTH')
    _bidirectional = ('approved', 'caption', 'description', 'collection_id')
    _get_by = ('id', 'collection_id')

    @classmethod
    def approved_kits(cls):
        return cls.from_query(cls._db_filter(approved=True).order_by('caption'))

    @classmethod
    def all_kits(cls):
        return cls._db_all()

    @property
    def description_html(self): return bbcode.render(self.description)

    @lazy_property
    def collection(self):
        return CollectionPrototype.get_by_id(self.collection_id)

    @classmethod
    def create(cls, collection, caption, description, approved=False):
        model = cls._model_class.objects.create(collection=collection._model,
                                                caption=caption,
                                                description=description,
                                                approved=approved)

        return cls(model=model)



class ItemPrototype(BasePrototype):
    _model_class = Item
    _readonly = ('id', 'created_at', 'updated_at', 'CAPTION_MAX_LENGTH')
    _bidirectional = ('approved',  'caption', 'text', 'kit_id')
    _get_by = ('id', 'kit_id')

    @lazy_property
    def kit(self):
        return KitPrototype.get_by_id(self.kit_id)

    @property
    def text_html(self): return bbcode.render(self.text)

    @classmethod
    def create(cls, kit, caption, text, approved=False):
        model = cls._model_class.objects.create(kit=kit._model,
                                                caption=caption,
                                                text=text,
                                                approved=approved)

        return cls(model=model)
