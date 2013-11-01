# coding: utf-8

from common.utils.prototypes import BasePrototype
from common.utils.decorators import lazy_property

from achievements.models import Section, Kit, Reward


class SectionPrototype(BasePrototype):
    _model_class = Section
    _readonly = ('id', 'created_at', 'updated_at', 'CAPTION_MAX_LENGTH', 'DESCRIPTION_MAX_LENGTH')
    _bidirectional = ('caption', 'description', 'approved', )
    _get_by = ('id', )

    @classmethod
    def approved_sections(cls):
        return cls.from_query(cls._db_filter(approved=True))

    @classmethod
    def all_sections(cls):
        return cls._db_all()

    @classmethod
    def create(cls, caption, description, approved=False):
        model = cls._model_class.objects.create(caption=caption,
                                                description=description,
                                                approved=approved)

        return cls(model=model)


class KitPrototype(BasePrototype):
    _model_class = Kit
    _readonly = ('id', 'created_at', 'updated_at', 'CAPTION_MAX_LENGTH', 'DESCRIPTION_MAX_LENGTH')
    _bidirectional = ('approved', 'caption', 'description', 'section_id')
    _get_by = ('id', 'section_id')

    @classmethod
    def approved_kits(cls):
        return cls.from_query(cls._db_filter(approved=True).order_by('caption'))

    @classmethod
    def all_kits(cls):
        return cls._db_all()

    @lazy_property
    def section(self):
        return SectionPrototype.get_by_id(self.section_id)

    @classmethod
    def create(cls, section, caption, description, approved=False):
        model = cls._model_class.objects.create(section=section._model,
                                                caption=caption,
                                                description=description,
                                                approved=approved)

        return cls(model=model)



class RewardPrototype(BasePrototype):
    _model_class = Reward
    _readonly = ('id', 'created_at', 'updated_at', 'CAPTION_MAX_LENGTH')
    _bidirectional = ('approved',  'caption', 'text', 'kit_id')
    _get_by = ('id', 'kit_id')

    @lazy_property
    def kit(self):
        return KitPrototype.get_by_id(self.kit_id)

    @classmethod
    def create(cls, kit, caption, text, approved=False):
        model = cls._model_class.objects.create(kit=kit._model,
                                                caption=caption,
                                                text=text,
                                                approved=approved)

        return cls(model=model)
