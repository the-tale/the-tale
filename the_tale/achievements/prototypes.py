# coding: utf-8

from common.utils.prototypes import BasePrototype

from achievements.models import Section, Kit, Reward


class SectionPrototype(BasePrototype):
    _model_class = Section
    _readonly = ('id', 'created_at', 'updated_at', 'caption', 'description', 'approved')
    _bidirectional = ()
    _get_by = ('id', )

    @classmethod
    def approved_sections(cls):
        return cls.from_query(cls._db_filter(approved=True))

    @classmethod
    def create(cls, caption, description):
        model = cls._model_class.create(caption=caption,
                                        description=description)

        return cls(model=model)


class KitPrototype(BasePrototype):
    _model_class = Kit
    _readonly = ('id', 'created_at', 'updated_at', 'caption', 'description', 'approved', 'section_id')
    _bidirectional = ()
    _get_by = ('id', )

    @classmethod
    def approved_kits(cls):
        return cls.from_query(cls._db_filter(approved=True))

    @classmethod
    def create(cls, section, caption, description):
        model = cls._model_class.create(section=section._model_class,
                                        caption=caption,
                                        description=description)

        return cls(model=model)



class RewardPrototype(BasePrototype):
    _model_class = Reward
    _readonly = ('id', 'created_at', 'updated_at', 'caption', 'text', 'approved')
    _bidirectional = ()
    _get_by = ('id', )


    @classmethod
    def create(cls, kit, caption, text):
        model = cls._model_class.create(kit=kit._model_class,
                                        caption=caption,
                                        text=text)

        return cls(model=model)
