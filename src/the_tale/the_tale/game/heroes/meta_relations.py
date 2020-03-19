
import smart_imports

smart_imports.all()


class Hero(meta_relations_objects.MetaType):
    __slots__ = ('caption', )
    TYPE = 9
    TYPE_CAPTION = 'Герой'

    def __init__(self, caption, **kwargs):
        super(Hero, self).__init__(**kwargs)
        self.caption = caption

    @property
    def url(self):
        return utils_urls.url('game:heroes:show', self.id)

    @classmethod
    def create_from_object(cls, hero):
        return cls(id=hero.id, caption=hero.name)

    @classmethod
    def create_removed(cls):
        return cls(id=None, caption='неизвестный герой')

    @classmethod
    def create_from_id(cls, id):
        from . import logic

        hero = logic.load_hero(hero_id=id)

        if hero is None:
            return cls.create_removed()

        return cls.create_from_object(hero)

    @classmethod
    def create_from_ids(cls, ids):
        records = models.Hero.objects.filter(id__in=ids)

        if len(ids) != len(records):
            raise meta_relations_exceptions.ObjectsNotFound(type=cls.TYPE, ids=ids)

        return [cls.create_from_object(logic.load_hero(hero_model=record)) for record in records]
