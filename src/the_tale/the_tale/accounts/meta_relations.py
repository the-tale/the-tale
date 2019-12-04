
import smart_imports

smart_imports.all()


class Account(meta_relations_objects.MetaType):
    __slots__ = ('caption', )
    TYPE = 7
    TYPE_CAPTION = 'Хранитель'

    def __init__(self, caption, **kwargs):
        super(Account, self).__init__(**kwargs)
        self.caption = caption

    @property
    def url(self):
        return utils_urls.url('accounts:show', self.id)

    @classmethod
    def create_from_object(cls, account):
        return cls(id=account.id, caption=account.nick_verbose)

    @classmethod
    def create_removed(cls, id):
        return cls(id=id, caption='неизвестный Хранитель')

    @classmethod
    def create_from_id(cls, id):
        from . import prototypes

        account = prototypes.AccountPrototype.get_by_id(id)

        if account is None:
            return cls.create_removed(id)

        return cls.create_from_object(account)

    @classmethod
    def create_from_ids(cls, ids):
        records = models.Account.objects.filter(id__in=ids)

        meta_objects = {}

        for record in records:
            meta_objects[record.id] = cls.create_from_object(prototypes.AccountPrototype(record))

        for id in ids:
            if id not in meta_objects:
                meta_objects[id] = cls.create_removed(id)

        return meta_objects.values()
